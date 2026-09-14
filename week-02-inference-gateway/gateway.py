"""Week 02 OpenAI-compatible inference gateway.

Run from the repository root while the Week 01 server is already listening on
port 8001:

    uv run --python .venv/bin/python uvicorn gateway:app \
      --app-dir week-02-inference-gateway --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Literal, Protocol

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field


BACKEND_URL = os.getenv("WEEK1_BACKEND_URL", "http://127.0.0.1:8001")
BACKEND_TIMEOUT_SECONDS = float(os.getenv("BACKEND_TIMEOUT_SECONDS", "45"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "64"))


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatCompletionRequest(BaseModel):
    """The stable, public request shape exposed to clients."""

    model: str = Field(min_length=1)
    messages: list[ChatMessage] = Field(min_length=1)
    max_tokens: int = Field(default=64, ge=1)
    stream: bool = False


class BackendGenerateRequest(BaseModel):
    """The private request shape expected by the Week 01 server."""

    messages: list[ChatMessage]
    max_new_tokens: int


@dataclass(frozen=True)
class BackendResult:
    text: str
    prompt_tokens: int
    output_tokens: int
    backend_model_id: str


class BackendTimeout(Exception):
    """The backend did not respond before the gateway deadline."""


class BackendFailure(Exception):
    """The backend returned an error or invalid response."""


class Backend(Protocol):
    async def generate(self, request: BackendGenerateRequest) -> BackendResult: ...

    async def stream(self, request: BackendGenerateRequest) -> AsyncIterator[str]: ...


def to_backend_request(request: ChatCompletionRequest) -> BackendGenerateRequest:
    """Translate the public `max_tokens` name to the Week 01 private name."""

    return BackendGenerateRequest(
        messages=request.messages,
        max_new_tokens=request.max_tokens,
    )


def public_response(
    result: BackendResult,
    *,
    request_id: str,
    model: str,
) -> dict[str, Any]:
    """Map a private backend result into a stable public chat response."""

    return {
        "id": request_id,
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.output_tokens,
            "total_tokens": result.prompt_tokens + result.output_tokens,
        },
    }


class HttpWeek1Backend:
    """Adapter that speaks the Week 01 server's private HTTP/SSE contract."""

    def __init__(
        self,
        base_url: str = BACKEND_URL,
        timeout_seconds: float = BACKEND_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def generate(self, request: BackendGenerateRequest) -> BackendResult:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
            ) as client:
                response = await client.post("/generate", json=request.model_dump())
            response.raise_for_status()
            body = response.json()
            return BackendResult(
                text=body["text"],
                prompt_tokens=int(body["prompt_tokens"]),
                output_tokens=int(body["output_tokens"]),
                backend_model_id=body["model_id"],
            )
        except httpx.TimeoutException as exc:
            raise BackendTimeout("The model backend did not respond before the deadline.") from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise BackendFailure("The model backend returned an invalid response.") from exc

    async def stream(self, request: BackendGenerateRequest) -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
            ) as client:
                async with client.stream(
                    "POST",
                    "/generate/stream",
                    json=request.model_dump(),
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        payload = line.removeprefix("data: ")
                        if payload == "[DONE]":
                            return
                        yield json.loads(payload)["text"]
        except httpx.TimeoutException as exc:
            raise BackendTimeout("The model backend did not respond before the deadline.") from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BackendFailure("The model backend returned an invalid stream.") from exc


@dataclass
class GatewayMetrics:
    registry: CollectorRegistry
    requests_total: Counter
    backend_errors_total: Counter
    request_duration_seconds: Histogram
    request_tokens_total: Counter
    in_flight_requests: Gauge


def create_metrics() -> GatewayMetrics:
    registry = CollectorRegistry()
    return GatewayMetrics(
        registry=registry,
        requests_total=Counter(
            "gateway_requests_total",
            "Gateway requests by response mode and outcome.",
            ["mode", "outcome"],
            registry=registry,
        ),
        backend_errors_total=Counter(
            "gateway_backend_errors_total",
            "Gateway backend errors by kind.",
            ["kind"],
            registry=registry,
        ),
        request_duration_seconds=Histogram(
            "gateway_request_duration_seconds",
            "End-to-end gateway request duration.",
            ["mode"],
            registry=registry,
        ),
        request_tokens_total=Counter(
            "gateway_request_tokens_total",
            "Prompt and completion token counts observed by the gateway.",
            ["direction"],
            registry=registry,
        ),
        in_flight_requests=Gauge(
            "gateway_in_flight_requests",
            "Requests currently being handled by the gateway.",
            registry=registry,
        ),
    )


def gateway_error(status_code: int, error_type: str, request_id: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"type": error_type, "request_id": request_id, "message": message},
    )


def create_gateway_app(
    backend: Backend,
    *,
    max_output_tokens: int = MAX_OUTPUT_TOKENS,
    metrics: GatewayMetrics | None = None,
) -> FastAPI:
    """Create a gateway app with an injectable backend for deterministic tests."""

    app = FastAPI(title="Week 02 Inference Gateway", version="0.1.0")
    app.state.backend = backend
    app.state.metrics = metrics or create_metrics()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "backend_url": getattr(backend, "base_url", "injected")}

    @app.get("/metrics")
    async def metrics_endpoint() -> Response:
        current_metrics: GatewayMetrics = app.state.metrics
        return Response(
            generate_latest(current_metrics.registry),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    @app.post("/v1/chat/completions")
    async def chat_completions(
        request: ChatCompletionRequest,
        http_request: Request,
    ) -> Any:
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        mode = "stream" if request.stream else "non_stream"
        current_metrics: GatewayMetrics = app.state.metrics

        if request.max_tokens > max_output_tokens:
            current_metrics.requests_total.labels(mode=mode, outcome="rejected").inc()
            raise gateway_error(
                400,
                "output_token_limit",
                request_id,
                f"max_tokens must be at most {max_output_tokens}.",
            )

        internal_request = to_backend_request(request)

        if request.stream:
            async def events() -> AsyncIterator[str]:
                started = time.perf_counter()
                current_metrics.in_flight_requests.inc()
                try:
                    async for text in backend.stream(internal_request):
                        if await http_request.is_disconnected():
                            current_metrics.requests_total.labels(mode=mode, outcome="cancelled").inc()
                            return
                        payload = {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "model": request.model,
                            "choices": [
                                {"index": 0, "delta": {"content": text}, "finish_reason": None}
                            ],
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                    current_metrics.requests_total.labels(mode=mode, outcome="success").inc()
                    # The Week 01 stream exposes text chunks but not final token
                    # counts. Do not label chunks as exact tokens; add final usage
                    # metadata to the backend protocol before exporting that metric.
                    yield "data: [DONE]\n\n"
                except BackendTimeout:
                    current_metrics.backend_errors_total.labels(kind="timeout").inc()
                    current_metrics.requests_total.labels(mode=mode, outcome="backend_timeout").inc()
                    error = {"type": "backend_timeout", "request_id": request_id}
                    yield f"event: error\ndata: {json.dumps(error)}\n\n"
                except BackendFailure:
                    current_metrics.backend_errors_total.labels(kind="failure").inc()
                    current_metrics.requests_total.labels(mode=mode, outcome="backend_failure").inc()
                    error = {"type": "backend_failure", "request_id": request_id}
                    yield f"event: error\ndata: {json.dumps(error)}\n\n"
                finally:
                    current_metrics.request_duration_seconds.labels(mode=mode).observe(
                        time.perf_counter() - started
                    )
                    current_metrics.in_flight_requests.dec()

            return StreamingResponse(
                events(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Request-ID": request_id},
            )

        started = time.perf_counter()
        current_metrics.in_flight_requests.inc()
        try:
            result = await backend.generate(internal_request)
            current_metrics.requests_total.labels(mode=mode, outcome="success").inc()
            current_metrics.request_tokens_total.labels(direction="prompt").inc(result.prompt_tokens)
            current_metrics.request_tokens_total.labels(direction="completion").inc(result.output_tokens)
            response = public_response(result, request_id=request_id, model=request.model)
            return response
        except BackendTimeout as exc:
            current_metrics.backend_errors_total.labels(kind="timeout").inc()
            current_metrics.requests_total.labels(mode=mode, outcome="backend_timeout").inc()
            raise gateway_error(504, "backend_timeout", request_id, str(exc)) from exc
        except BackendFailure as exc:
            current_metrics.backend_errors_total.labels(kind="failure").inc()
            current_metrics.requests_total.labels(mode=mode, outcome="backend_failure").inc()
            raise gateway_error(502, "backend_failure", request_id, str(exc)) from exc
        finally:
            current_metrics.request_duration_seconds.labels(mode=mode).observe(
                time.perf_counter() - started
            )
            current_metrics.in_flight_requests.dec()

    return app


app = create_gateway_app(HttpWeek1Backend())
