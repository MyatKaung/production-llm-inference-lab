"""Benchmark the public gateway with streaming requests.

This script records user-visible TTFT and total latency. It intentionally does
not relabel either measure as pure model prefill or pure decode time: the client
sees gateway, backend, network, and stream-delivery overhead together.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parent
DEFAULT_RESULTS = ROOT / "results"


def percentile(values: list[float], fraction: float) -> float | None:
    """Nearest-rank percentile; returns None when there are no successful samples."""

    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def prompt_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [record for record in records if record["success"]]
    ttfts = [record["ttft_seconds"] for record in successful if record["ttft_seconds"] is not None]
    totals = [record["total_latency_seconds"] for record in successful]
    return {
        "requests": len(records),
        "successful_requests": len(successful),
        "failed_requests": len(records) - len(successful),
        "ttft_p50_seconds": percentile(ttfts, 0.50),
        "ttft_p95_seconds": percentile(ttfts, 0.95),
        "total_p50_seconds": percentile(totals, 0.50),
        "total_p95_seconds": percentile(totals, 0.95),
    }


def parse_gateway_metrics(text: str) -> dict[str, float | None]:
    """Extract only the metrics we can interpret without inventing queue time."""

    in_flight: float | None = None
    backend_errors = 0.0
    for line in text.splitlines():
        if line.startswith("gateway_in_flight_requests "):
            in_flight = float(line.rsplit(" ", 1)[1])
        elif line.startswith("gateway_backend_errors_total"):
            backend_errors += float(line.rsplit(" ", 1)[1])
    return {"in_flight": in_flight, "backend_errors_total": backend_errors}


class PromptFactory:
    """Build repeatable long prompts and optionally count their exact chat tokens."""

    def __init__(self, tokenizer_id: str | None) -> None:
        self.tokenizer = None
        if tokenizer_id:
            from transformers import AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)

    def count_prompt_tokens(self, messages: list[dict[str, str]]) -> int | None:
        if self.tokenizer is None:
            return None
        tokens = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
        )
        # Transformers versions may return a plain list, a tensor, or a
        # BatchEncoding-like mapping. Count actual token IDs, never mapping
        # keys such as `input_ids` and `attention_mask`.
        if isinstance(tokens, Mapping):
            tokens = tokens["input_ids"]
        if hasattr(tokens, "tolist"):
            tokens = tokens.tolist()
        if tokens and isinstance(tokens[0], list):
            tokens = tokens[0]
        return len(tokens)

    def make_messages(self, target_tokens: int) -> tuple[list[dict[str, str]], int | None]:
        phrase = "alpha beta gamma delta. "
        prefix = "This is a fixed benchmark context. Read it, then answer with the word acknowledged.\n\n"

        def messages_for(repetitions: int) -> list[dict[str, str]]:
            return [{"role": "user", "content": prefix + phrase * repetitions}]

        if self.tokenizer is None:
            repetitions = max(1, math.ceil(target_tokens / 4))
            messages = messages_for(repetitions)
            return messages, None

        # Find the closest repeat count without pretending that character count
        # equals model-token count. The remaining small difference is recorded.
        low, high = 0, max(1, target_tokens * 2)
        while low < high:
            middle = (low + high) // 2
            if self.count_prompt_tokens(messages_for(middle)) < target_tokens:
                low = middle + 1
            else:
                high = middle
        candidates = [max(0, low - 1), low]
        messages = min(
            (messages_for(candidate) for candidate in candidates),
            key=lambda item: abs((self.count_prompt_tokens(item) or 0) - target_tokens),
        )
        return messages, self.count_prompt_tokens(messages)


async def one_streaming_request(
    client: httpx.AsyncClient,
    gateway_url: str,
    payload: dict[str, Any],
    *,
    start_gate: asyncio.Event,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Send one request after the shared gate opens and measure its SSE lifecycle."""

    await start_gate.wait()
    started = time.perf_counter()
    first_delta_at: float | None = None
    request_id: str | None = None
    chunks: list[str] = []
    stream_error: str | None = None
    status_code: int | None = None
    saw_done = False
    event_name: str | None = None

    try:
        async with client.stream(
            "POST",
            f"{gateway_url.rstrip('/')}/v1/chat/completions",
            json=payload,
        ) as response:
            status_code = response.status_code
            request_id = response.headers.get("X-Request-ID")
            if response.status_code != 200:
                body = await response.aread()
                stream_error = body.decode("utf-8", errors="replace")
            else:
                async for line in response.aiter_lines():
                    if line.startswith("event: "):
                        event_name = line.removeprefix("event: ")
                        continue
                    if not line.startswith("data: "):
                        continue
                    event = line.removeprefix("data: ")
                    now = time.perf_counter()
                    if event == "[DONE]":
                        saw_done = True
                        break
                    try:
                        body = json.loads(event)
                    except json.JSONDecodeError:
                        stream_error = "gateway emitted malformed SSE JSON"
                        break
                    request_id = body.get("id", request_id)
                    if event_name == "error" or body.get("type"):
                        stream_error = body.get("type", "gateway stream error")
                        break
                    if first_delta_at is None:
                        first_delta_at = now
                    choice = body.get("choices", [{}])[0]
                    chunks.append(choice.get("delta", {}).get("content", ""))
                    event_name = None
    except httpx.HTTPError as exc:
        stream_error = f"{type(exc).__name__}: {exc}"

    finished = time.perf_counter()
    return {
        **metadata,
        "status_code": status_code,
        "success": status_code == 200 and saw_done and stream_error is None,
        "request_id": request_id,
        "ttft_seconds": None if first_delta_at is None else first_delta_at - started,
        "total_latency_seconds": finished - started,
        "stream_event_count": len(chunks),
        "output_characters": len("".join(chunks)),
        "output_tokens": None,
        "output_tokens_note": "unavailable: current gateway streaming contract has no final usage event",
        "error": stream_error,
    }


async def run_wave(
    client: httpx.AsyncClient,
    gateway_url: str,
    payload: dict[str, Any],
    metadata: dict[str, Any],
    request_count: int,
) -> list[dict[str, Any]]:
    """Open one shared start gate so a wave begins as concurrently as Python allows."""

    start_gate = asyncio.Event()
    tasks = [
        asyncio.create_task(
            one_streaming_request(
                client,
                gateway_url,
                payload,
                start_gate=start_gate,
                metadata={**metadata, "request_in_wave": index + 1},
            )
        )
        for index in range(request_count)
    ]
    start_gate.set()
    return await asyncio.gather(*tasks)


async def sample_metrics(
    client: httpx.AsyncClient,
    gateway_url: str,
    stop: asyncio.Event,
    interval_seconds: float,
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    while not stop.is_set():
        observed_at = time.perf_counter()
        try:
            response = await client.get(f"{gateway_url.rstrip('/')}/metrics")
            response.raise_for_status()
            sample = parse_gateway_metrics(response.text)
            samples.append({"seconds": observed_at, **sample})
        except httpx.HTTPError as exc:
            samples.append({"seconds": observed_at, "metrics_error": f"{type(exc).__name__}: {exc}"})
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
        except TimeoutError:
            pass
    return samples


async def run_cell(
    client: httpx.AsyncClient,
    gateway_url: str,
    *,
    model: str,
    messages: list[dict[str, str]],
    actual_prompt_tokens: int | None,
    prompt_length_target: int,
    concurrency: int,
    max_tokens: int,
    warmup_waves: int,
    measured_waves: int,
    metrics_interval_seconds: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": True}
    base = {
        "prompt_length_target": prompt_length_target,
        "actual_prompt_tokens": actual_prompt_tokens,
        "concurrency": concurrency,
        "max_tokens": max_tokens,
    }

    for wave in range(warmup_waves):
        await run_wave(
            client,
            gateway_url,
            payload,
            {**base, "phase": "warmup", "wave": wave + 1},
            concurrency,
        )

    stop_sampling = asyncio.Event()
    sampler = asyncio.create_task(
        sample_metrics(client, gateway_url, stop_sampling, metrics_interval_seconds)
    )
    records: list[dict[str, Any]] = []
    stopped_reason: str | None = None
    try:
        for wave in range(measured_waves):
            wave_records = await run_wave(
                client,
                gateway_url,
                payload,
                {**base, "phase": "measured", "wave": wave + 1},
                concurrency,
            )
            records.extend(wave_records)
            if any(not record["success"] for record in wave_records):
                stopped_reason = "a measured wave contained failed requests"
                break
    finally:
        # Let the gateway finish its error/cleanup bookkeeping before the final
        # metric sample. Without this grace period a client can see an SSE error
        # before Prometheus exposes the corresponding counter increment.
        await asyncio.sleep(metrics_interval_seconds)
        stop_sampling.set()
    samples = await sampler
    return records, samples, stopped_reason


def metrics_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    in_flight = [sample["in_flight"] for sample in samples if sample.get("in_flight") is not None]
    error_counts = [sample["backend_errors_total"] for sample in samples if sample.get("backend_errors_total") is not None]
    return {
        "sample_count": len(samples),
        "peak_in_flight": max(in_flight) if in_flight else None,
        "backend_errors_before": error_counts[0] if error_counts else None,
        "backend_errors_after": error_counts[-1] if error_counts else None,
        "queue_time_seconds": None,
        "queue_time_note": "unavailable: current gateway has no explicit admission queue timer",
        "samples": samples,
    }


async def main_async(args: argparse.Namespace) -> int:
    factory = PromptFactory(None if args.no_tokenizer else args.tokenizer_id)
    if args.mode == "matrix":
        # Finish concurrency-1 cells first. On a constrained local machine this
        # preserves useful long-prompt evidence before the first pressure wave.
        cells = [
            (length, concurrency, args.measured_waves)
            for concurrency in args.concurrencies
            for length in args.prompt_lengths
        ]
    else:
        cells = [(args.pressure_prompt_length, args.pressure_concurrency, args.pressure_waves)]

    output_path = args.output or args.results_dir / f"{args.label}-matrix.jsonl"
    metrics_path = args.metrics_output or args.results_dir / f"{args.label}-metrics.json"
    if output_path.exists() and not args.overwrite:
        raise FileExistsError(f"{output_path} already exists; choose a new --label or pass --overwrite")

    timeout = httpx.Timeout(args.request_timeout_seconds, connect=10.0)
    all_records: list[dict[str, Any]] = []
    cell_reports: list[dict[str, Any]] = []
    aborted_reason: str | None = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        for prompt_length, concurrency, measured_waves in cells:
            messages, actual_tokens = factory.make_messages(prompt_length)
            records, samples, stopped_reason = await run_cell(
                client,
                args.gateway_url,
                model=args.model,
                messages=messages,
                actual_prompt_tokens=actual_tokens,
                prompt_length_target=prompt_length,
                concurrency=concurrency,
                max_tokens=args.max_tokens,
                warmup_waves=args.warmup_waves,
                measured_waves=measured_waves,
                metrics_interval_seconds=args.metrics_interval_seconds,
            )
            all_records.extend(records)
            cell_reports.append(
                {
                    "prompt_length_target": prompt_length,
                    "actual_prompt_tokens": actual_tokens,
                    "concurrency": concurrency,
                    "metrics": prompt_metrics(records),
                    "gateway_metrics": metrics_summary(samples),
                    "stopped_reason": stopped_reason,
                }
            )
            print(
                f"prompt≈{prompt_length}, concurrency={concurrency}: "
                f"{sum(record['success'] for record in records)}/{len(records)} succeeded"
            )
            if stopped_reason and not args.continue_after_failure:
                aborted_reason = (
                    f"stopped after prompt≈{prompt_length}, concurrency={concurrency}: {stopped_reason}"
                )
                print(aborted_reason)
                break

    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in all_records),
        encoding="utf-8",
    )
    metrics_path.write_text(
        json.dumps(
            {
                "label": args.label,
                "gateway_url": args.gateway_url,
                "mode": args.mode,
                "aborted_reason": aborted_reason,
                "cells": cell_reports,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output_path}")
    print(f"wrote {metrics_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Week 3 streaming gateway benchmarks.")
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="local-qwen")
    parser.add_argument("--tokenizer-id", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--no-tokenizer", action="store_true", help="Record prompt token count as unavailable.")
    parser.add_argument("--mode", choices=["matrix", "pressure"], default="matrix")
    parser.add_argument("--prompt-lengths", nargs="+", type=int, default=[128, 1024, 4096])
    parser.add_argument("--concurrencies", nargs="+", type=int, default=[1, 4, 16])
    parser.add_argument("--warmup-waves", type=int, default=2)
    parser.add_argument("--measured-waves", type=int, default=10)
    parser.add_argument("--pressure-prompt-length", type=int, default=4096)
    parser.add_argument("--pressure-concurrency", type=int, default=16)
    parser.add_argument("--pressure-waves", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--metrics-interval-seconds", type=float, default=0.10)
    parser.add_argument("--request-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--label", default="baseline")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--metrics-output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--continue-after-failure",
        action="store_true",
        help="Continue after a failed wave. Use only when the backend is known to remain healthy.",
    )
    args = parser.parse_args()
    if any(value < 1 for value in [args.warmup_waves, args.measured_waves, args.max_tokens]):
        parser.error("warmup waves, measured waves, and max tokens must all be at least 1")
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
