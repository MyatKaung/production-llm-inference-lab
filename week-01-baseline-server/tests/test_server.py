import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1]))
import server  # noqa: E402


class FakeStreamer:
    tokenizer = None

    def __iter__(self):
        yield ("token", 10, 1.0)
        yield ("token", 11, 1.1)


class FakeEngine:
    model_id = "fake-model"
    device = "test"

    def generate(self, request):
        return {
            "text": "hello",
            "prompt_tokens": 4,
            "output_tokens": 1,
            "total_latency_seconds": 0.01,
            "output_tokens_per_second": 100.0,
            "model_id": self.model_id,
            "device": self.device,
        }

    def stream(self, request):
        streamer = FakeStreamer()
        streamer.tokenizer = FakeTokenizer()
        return streamer


class FakeTokenizer:
    def decode(self, token_ids, skip_special_tokens=True):
        return {10: "hello", 11: " world"}[token_ids[0]]


@pytest.fixture()
def client():
    old_engine = server.engine
    server.engine = FakeEngine()
    try:
        with TestClient(server.app) as test_client:
            yield test_client
    finally:
        server.engine = old_engine


def payload(**overrides):
    value = {
        "messages": [{"role": "user", "content": "Say hello."}],
        "max_new_tokens": 16,
    }
    value.update(overrides)
    return value


def test_health_reports_loaded_engine(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_loaded": True,
        "model_id": "fake-model",
        "device": "test",
    }


def test_generate_returns_json(client):
    response = client.post("/generate", json=payload())
    assert response.status_code == 200
    assert response.json()["text"] == "hello"
    assert response.json()["output_tokens"] == 1


def test_stream_returns_ordered_sse_events_and_done(client):
    response = client.post("/generate/stream", json=payload())
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert '"index": 0' in response.text
    assert '"text": "hello"' in response.text
    assert '"index": 1' in response.text
    assert '"text": " world"' in response.text
    assert response.text.rstrip().endswith("data: [DONE]")


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"messages": []},
        {"messages": [{"role": "user", "content": ""}]},
        {"messages": [{"role": "invalid", "content": "hello"}]},
        {"messages": [{"role": "user", "content": "hello"}], "max_new_tokens": 0},
    ],
)
def test_invalid_requests_return_422(client, bad_payload):
    response = client.post("/generate", json=bad_payload)
    assert response.status_code == 422
