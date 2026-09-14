"""Deterministic, inspectable scoring for the Week 3 fixed evaluation set.

This scorer deliberately uses simple rules such as text containment and JSON
parsing. It never asks another language model to judge an answer, so identical
input text always produces identical pass/fail output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / "eval" / "cases.jsonl"
DEFAULT_EXPECTED = ROOT / "eval" / "expected-results.json"


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Load one JSON object per line and require unique case IDs."""

    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        case = json.loads(line)
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{path}:{line_number} needs a non-empty string id")
        if case_id in seen_ids:
            raise ValueError(f"duplicate evaluation case id: {case_id}")
        seen_ids.add(case_id)
        cases.append(case)
    return cases


def load_expected(path: Path) -> dict[str, dict[str, Any]]:
    expected = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(expected, dict):
        raise ValueError("expected-results must contain an object keyed by case ID")
    return expected


def _normalised(text: str) -> str:
    return text.casefold().strip()


def score_completion(case_id: str, completion: str, expected: dict[str, Any]) -> dict[str, Any]:
    """Return a stable, human-readable pass/fail result for one completion."""

    text = completion or ""
    normalised = _normalised(text)
    failures: list[str] = []

    for required in expected.get("contains", []):
        if _normalised(str(required)) not in normalised:
            failures.append(f"missing required text: {required!r}")

    for forbidden in expected.get("not_contains", []):
        if _normalised(str(forbidden)) in normalised:
            failures.append(f"contains forbidden text: {forbidden!r}")

    contains_any = expected.get("contains_any", [])
    if contains_any and not any(_normalised(str(option)) in normalised for option in contains_any):
        failures.append(f"missing one of: {contains_any!r}")

    for options in expected.get("contains_any_groups", []):
        if not any(_normalised(str(option)) in normalised for option in options):
            failures.append(f"missing one of: {options!r}")

    max_words = expected.get("max_words")
    if max_words is not None and len(text.split()) > int(max_words):
        failures.append(f"has more than {max_words} word(s)")

    parsed_json: Any = None
    json_required = expected.get("valid_json") or expected.get("json_fields")
    if json_required:
        try:
            parsed_json = json.loads(text.strip())
        except json.JSONDecodeError:
            failures.append("response is not valid JSON")
        else:
            if not isinstance(parsed_json, dict):
                failures.append("JSON response is not an object")
            else:
                for key, value in expected.get("json_fields", {}).items():
                    if parsed_json.get(key) != value:
                        failures.append(f"JSON field {key!r} was not {value!r}")

    return {
        "id": case_id,
        "passed": not failures,
        "failures": failures,
        "completion": text,
    }


def score_responses(
    cases: list[dict[str, Any]],
    expected_by_id: dict[str, dict[str, Any]],
    responses_by_id: dict[str, str],
) -> dict[str, Any]:
    """Score every fixed case, including an explicit failure for missing output."""

    results: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["id"]
        if case_id not in expected_by_id:
            raise ValueError(f"missing expected rule for {case_id}")
        if case_id not in responses_by_id:
            results.append(
                {
                    "id": case_id,
                    "passed": False,
                    "failures": ["no completion was recorded"],
                    "completion": "",
                }
            )
            continue
        results.append(score_completion(case_id, responses_by_id[case_id], expected_by_id[case_id]))

    passed = sum(result["passed"] for result in results)
    return {
        "passed": passed,
        "total": len(results),
        "score": passed / len(results) if results else 0.0,
        "results": results,
    }


def _responses_from_run(path: Path) -> dict[str, str]:
    """Read a `quality_gate.py` run artifact."""

    run = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(run, dict) or not isinstance(run.get("results"), list):
        raise ValueError("responses file must be a quality_gate.py JSON artifact")
    return {
        str(result["id"]): str(result.get("completion", ""))
        for result in run["results"]
        if isinstance(result, dict) and "id" in result and result.get("status_code") == 200
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a completed Week 3 quality-gate run.")
    parser.add_argument("--responses", required=True, type=Path, help="JSON artifact from quality_gate.py")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--output", type=Path, help="Optional JSON score report path")
    args = parser.parse_args()

    report = score_responses(
        load_cases(args.cases),
        load_expected(args.expected),
        _responses_from_run(args.responses),
    )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
