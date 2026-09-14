import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import scorer  # noqa: E402


def test_case_and_expected_files_have_the_same_ids():
    cases = scorer.load_cases(scorer.DEFAULT_CASES)
    expected = scorer.load_expected(scorer.DEFAULT_EXPECTED)

    assert {case["id"] for case in cases} == set(expected)
    assert len(cases) == 10


def test_json_rule_passes_only_for_the_expected_object():
    expected = {"valid_json": True, "json_fields": {"city": "Singapore", "year": 2024}}

    passed = scorer.score_completion("json-01", '{"city": "Singapore", "year": 2024}', expected)
    failed = scorer.score_completion("json-01", "The city is Singapore in 2024.", expected)

    assert passed["passed"] is True
    assert failed["passed"] is False
    assert "response is not valid JSON" in failed["failures"]


def test_score_is_repeatable_for_identical_text():
    expected = {"contains": ["singapore"], "not_contains": ["kuala lumpur"]}

    first = scorer.score_completion("extract-city-01", "Singapore", expected)
    second = scorer.score_completion("extract-city-01", "Singapore", expected)

    assert first == second


def test_missing_completion_is_an_explicit_failure():
    report = scorer.score_responses(
        [{"id": "case-1"}],
        {"case-1": {"contains": ["ok"]}},
        {},
    )

    assert report["passed"] == 0
    assert report["results"][0]["failures"] == ["no completion was recorded"]
