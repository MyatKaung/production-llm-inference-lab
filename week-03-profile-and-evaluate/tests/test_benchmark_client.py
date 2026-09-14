import sys
from collections import UserDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import benchmark_client  # noqa: E402


def test_percentile_uses_nearest_rank():
    values = [0.4, 0.1, 0.3, 0.2]

    assert benchmark_client.percentile(values, 0.50) == 0.2
    assert benchmark_client.percentile(values, 0.95) == 0.4
    assert benchmark_client.percentile([], 0.95) is None


def test_metrics_parser_keeps_queue_time_out_of_the_result():
    metrics = """# HELP gateway_in_flight_requests Requests currently being handled\n""" \
        "gateway_in_flight_requests 4.0\n" \
        "gateway_backend_errors_total{kind=\"timeout\"} 2.0\n" \
        "gateway_backend_errors_total{kind=\"failure\"} 1.0\n"

    parsed = benchmark_client.parse_gateway_metrics(metrics)

    assert parsed == {"in_flight": 4.0, "backend_errors_total": 3.0}


def test_prompt_metrics_excludes_failed_requests_from_latency_percentiles():
    summary = benchmark_client.prompt_metrics(
        [
            {"success": True, "ttft_seconds": 0.2, "total_latency_seconds": 1.0},
            {"success": True, "ttft_seconds": 0.4, "total_latency_seconds": 2.0},
            {"success": False, "ttft_seconds": None, "total_latency_seconds": 3.0},
        ]
    )

    assert summary["successful_requests"] == 2
    assert summary["failed_requests"] == 1
    assert summary["ttft_p50_seconds"] == 0.2
    assert summary["total_p95_seconds"] == 2.0


def test_prompt_factory_counts_ids_inside_mapping_not_mapping_keys():
    class BatchEncodingLike(UserDict):
        pass

    class FakeTokenizer:
        def apply_chat_template(self, *args, **kwargs):
            return BatchEncodingLike({"input_ids": [11, 12, 13, 14]})

    factory = benchmark_client.PromptFactory(None)
    factory.tokenizer = FakeTokenizer()

    assert factory.count_prompt_tokens([{"role": "user", "content": "hello"}]) == 4
