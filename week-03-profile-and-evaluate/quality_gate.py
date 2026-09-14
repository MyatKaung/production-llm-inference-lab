"""Run the fixed evaluation set through the public Week 2 gateway.

The gateway is deliberately the only HTTP target. This keeps the quality gate
aligned with the system a client actually uses.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from scorer import DEFAULT_CASES, DEFAULT_EXPECTED, load_cases, load_expected, score_responses


ROOT = Path(__file__).resolve().parent
DEFAULT_RESULTS = ROOT / "results"


def call_gateway(
    gateway_url: str,
    *,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    """Make one non-streaming public request and return a serializable record."""

    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{gateway_url.rstrip('/')}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
            return {
                "status_code": response.status,
                "request_id": response.headers.get("X-Request-ID", body.get("id")),
                "completion": body["choices"][0]["message"]["content"],
                "usage": body.get("usage"),
                "total_latency_seconds": time.perf_counter() - started,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "status_code": exc.code,
            "request_id": exc.headers.get("X-Request-ID") if exc.headers else None,
            "completion": "",
            "usage": None,
            "total_latency_seconds": time.perf_counter() - started,
            "error": exc.read().decode("utf-8", errors="replace"),
        }
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as exc:
        return {
            "status_code": None,
            "request_id": None,
            "completion": "",
            "usage": None,
            "total_latency_seconds": time.perf_counter() - started,
            "error": f"{type(exc).__name__}: {exc}",
        }


def comparable_outcomes(report: dict[str, Any]) -> tuple[int, int, tuple[tuple[str, bool], ...]]:
    return (
        int(report["passed"]),
        int(report["total"]),
        tuple((result["id"], bool(result["passed"])) for result in report["results"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic Week 3 quality gate.")
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="local-qwen")
    parser.add_argument("--label", default="baseline-run-1")
    parser.add_argument("--timeout-seconds", type=float, default=45.0)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--compare-with",
        type=Path,
        help="Earlier quality-gate JSON artifact; return non-zero if pass/fail outcomes differ.",
    )
    args = parser.parse_args()

    cases = load_cases(args.cases)
    expected = load_expected(args.expected)
    raw_results: list[dict[str, Any]] = []
    for case in cases:
        result = call_gateway(
            args.gateway_url,
            model=args.model,
            messages=case["messages"],
            max_tokens=int(case.get("max_tokens", 64)),
            timeout_seconds=args.timeout_seconds,
        )
        raw_results.append({"id": case["id"], "category": case["category"], **result})
        outcome = "ok" if result["status_code"] == 200 else "error"
        print(f"{case['id']}: {outcome}")

    responses = {
        result["id"]: result["completion"]
        for result in raw_results
        if result["status_code"] == 200
    }
    score = score_responses(cases, expected, responses)
    report = {
        "label": args.label,
        "gateway_url": args.gateway_url,
        "generation": {"model": args.model, "do_sample": False},
        "score": score,
        "results": raw_results,
    }
    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / f"quality-{args.label}.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"quality score: {score['passed']}/{score['total']} ({score['score']:.0%})")
    print(f"wrote {output_path}")

    if args.compare_with:
        previous = json.loads(args.compare_with.read_text(encoding="utf-8"))["score"]
        if comparable_outcomes(score) != comparable_outcomes(previous):
            print("quality gate changed: inspect the two artifacts before optimizing")
            return 2
        print("quality gate is repeatable: same case outcomes as the earlier run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
