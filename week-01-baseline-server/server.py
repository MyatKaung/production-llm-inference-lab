"""Small Hugging Face inference server for Week 01.

Run from the repository root with:

    uv run --python .venv/bin/python uvicorn server:app \
      --app-dir week-01-baseline-server --host 127.0.0.1 --port 8001
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path
from queue import Queue
from typing import Any, Iterator, Literal

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import BaseStreamer


MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "64"))


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class GenerateRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    max_new_tokens: int = Field(default=64, ge=1)


class InferenceEngine:
    """Owns one tokenizer/model pair and provides generation operations."""

    def __init__(self, model_id: str = MODEL_ID) -> None:
        self.model_id = model_id
        self.device = self._choose_device()
        dtype = torch.float16 if self.device in {"mps", "cuda"} else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
        ).to(self.device)
        self.model.eval()

    @staticmethod
    def _choose_device() -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _synchronize(self) -> None:
        if self.device == "cuda":
            torch.cuda.synchronize()
        elif self.device == "mps":
            torch.mps.synchronize()

    def make_inputs(self, messages: list[Message]) -> dict[str, torch.Tensor]:
        chat = [message.model_dump() for message in messages]
        encoded = self.tokenizer.apply_chat_template(
            chat,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        return {key: value.to(self.device) for key, value in encoded.items()}

    @torch.inference_mode()
    def generate(self, request: GenerateRequest) -> dict[str, Any]:
        inputs = self.make_inputs(request.messages)
        self._synchronize()
        started = time.perf_counter()
        output = self.model.generate(
            **inputs,
            max_new_tokens=min(request.max_new_tokens, MAX_NEW_TOKENS),
            do_sample=False,
            use_cache=True,
        )
        self._synchronize()
        elapsed = time.perf_counter() - started
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        new_tokens = output[0, prompt_tokens:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        output_tokens = int(new_tokens.shape[-1])
        return {
            "text": text,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_latency_seconds": elapsed,
            "output_tokens_per_second": output_tokens / elapsed if elapsed else None,
            "model_id": self.model_id,
            "device": self.device,
        }

    def stream(self, request: GenerateRequest) -> "TokenQueueStreamer":
        inputs = self.make_inputs(request.messages)
        streamer = TokenQueueStreamer(self.tokenizer)
        kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=min(request.max_new_tokens, MAX_NEW_TOKENS),
            do_sample=False,
            use_cache=True,
        )

        def run() -> None:
            try:
                self._synchronize()
                with torch.inference_mode():
                    self.model.generate(**kwargs)
                self._synchronize()
            except Exception as exc:  # communicate worker failure to the reader
                streamer.fail(exc)

        threading.Thread(target=run, daemon=True).start()
        return streamer


class TokenQueueStreamer(BaseStreamer):
    """Receives generated token IDs and exposes them to an HTTP iterator."""

    def __init__(self, tokenizer: Any) -> None:
        self.tokenizer = tokenizer
        self.queue: Queue[tuple[str, Any, float]] = Queue()
        self.skip_prompt = True

    def put(self, value: torch.Tensor) -> None:
        if value.ndim == 1:
            value = value.unsqueeze(0)
        if self.skip_prompt:
            self.skip_prompt = False
            return
        for token_id in value[0].tolist():
            self.queue.put(("token", int(token_id), time.perf_counter()))

    def end(self) -> None:
        self.queue.put(("end", None, time.perf_counter()))

    def fail(self, error: Exception) -> None:
        self.queue.put(("error", error, time.perf_counter()))

    def __iter__(self) -> Iterator[tuple[str, Any, float]]:
        while True:
            event = self.queue.get()
            if event[0] == "end":
                return
            if event[0] == "error":
                raise event[1]
            yield event


app = FastAPI(title="Week 01 Hugging Face Inference Server", version="0.1.0")
engine: InferenceEngine | None = None


def get_engine() -> InferenceEngine:
    global engine
    if engine is None:
        engine = InferenceEngine()
    return engine


@app.get("/health")
def health() -> dict[str, Any]:
    loaded = engine is not None
    return {
        "status": "ok",
        "model_loaded": loaded,
        "model_id": engine.model_id if engine else MODEL_ID,
        "device": engine.device if engine else None,
    }


@app.post("/generate")
def generate(request: GenerateRequest) -> dict[str, Any]:
    try:
        return get_engine().generate(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest, http_request: Request) -> StreamingResponse:
    streamer = get_engine().stream(request)
    request_id = str(uuid.uuid4())

    def events() -> Iterator[str]:
        for index, (kind, token_id, timestamp) in enumerate(streamer):
            token_text = streamer.tokenizer.decode([token_id], skip_special_tokens=True)
            payload = {
                "request_id": request_id,
                "index": index,
                "token_id": token_id,
                "text": token_text,
                "timestamp": timestamp,
            }
            yield f"data: {json.dumps(payload)}\n\n"
        yield "data: [DONE]\n\n"

    async def guarded_events() -> Iterator[str]:
        # The worker cannot be cancelled safely at this layer yet. This check
        # prevents sending more events after a disconnected client.
        for event in events():
            if await http_request.is_disconnected():
                return
            yield event

    return StreamingResponse(
        guarded_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Request-ID": request_id},
    )


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})
