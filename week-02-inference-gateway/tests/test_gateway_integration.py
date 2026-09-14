"""Optional real integration tests.

Start the Week 01 server on port 8001, then run:

    RUN_WEEK1_INTEGRATION=1 uv run --python .venv/bin/python pytest \
      week-02-inference-gateway/tests/test_gateway_integration.py -q
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1]))
import gateway  # noqa: E402


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_WEEK1_INTEGRATION") != "1",
    reason="Set RUN_WEEK1_INTEGRATION=1 after starting the Week 01 server on port 8001.",
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(gateway.create_gateway_app(gateway.HttpWeek1Backend()))


def payload(stream: bool = False) -> dict:
    return {
        "model": "local-qwen",
        "messages": [{"role": "user", "content": "Explain caching in one sentence."}],
        "max_tokens": 8,
        "stream": stream,
    }


def test_real_backend_non_streaming(client: TestClient):
    response = client.post("/v1/chat/completions", json=payload())
    response.raise_for_status()
    body = response.json()
    assert body["id"].startswith("req_")
    assert body["choices"][0]["message"]["content"]
    assert body["usage"]["prompt_tokens"] > 0


def test_real_backend_streaming(client: TestClient):
    response = client.post("/v1/chat/completions", json=payload(stream=True))
    response.raise_for_status()
    events = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    assert events[-1] == "[DONE]"
    assert events[:-1]
