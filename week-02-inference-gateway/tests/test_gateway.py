import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncIterator

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1]))
import gateway  # noqa: E402


@dataclass
class FakeBackend:
    result: gateway.BackendResult = field(
        default_factory=lambda: gateway.BackendResult(
            text="Caching stores reusable data.",
            prompt_tokens=11,
            output_tokens=5,
            backend_model_id="fake-qwen",
        )
    )
    error: Exception | None = None
    chunks: list[str] = field(default_factory=lambda: ["C", "aching"])
    calls: list[gateway.BackendGenerateRequest] = field(default_factory=list)

    async def generate(self, request: gateway.BackendGenerateRequest) -> gateway.BackendResult:
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.result

    async def stream(self, request: gateway.BackendGenerateRequest) -> AsyncIterator[str]:
        self.calls.append(request)
        if self.error:
            raise self.error
        for chunk in self.chunks:
            yield chunk


@pytest.fixture()
def fake_backend() -> FakeBackend:
    return FakeBackend()


@pytest.fixture()
def client(fake_backend: FakeBackend) -> TestClient:
    with TestClient(gateway.create_gateway_app(fake_backend, max_output_tokens=64)) as test_client:
        yield test_client


def payload(**overrides):
    body = {
        "model": "local-qwen",
        "messages": [{"role": "user", "content": "What is caching?"}],
        "max_tokens": 16,
    }
    body.update(overrides)
    return body


def test_health_exposes_only_gateway_state(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_non_streaming_response_maps_private_backend_to_public_contract(
    client: TestClient, fake_backend: FakeBackend
):
    response = client.post("/v1/chat/completions", json=payload())

    assert response.status_code == 200
    body = response.json()
    assert body["id"].startswith("req_")
    assert body["object"] == "chat.completion"
    assert body["model"] == "local-qwen"
    assert body["choices"][0]["message"] == {
        "role": "assistant",
        "content": "Caching stores reusable data.",
    }
    assert body["usage"] == {
        "prompt_tokens": 11,
        "completion_tokens": 5,
        "total_tokens": 16,
    }
    assert fake_backend.calls[0].max_new_tokens == 16


def test_limit_rejection_does_not_call_backend(client: TestClient, fake_backend: FakeBackend):
    response = client.post("/v1/chat/completions", json=payload(max_tokens=65))

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["type"] == "output_token_limit"
    assert detail["request_id"].startswith("req_")
    assert fake_backend.calls == []


def test_timeout_maps_to_controlled_504(fake_backend: FakeBackend):
    fake_backend.error = gateway.BackendTimeout("simulated timeout")
    client = TestClient(gateway.create_gateway_app(fake_backend))

    response = client.post("/v1/chat/completions", json=payload())

    assert response.status_code == 504
    assert response.json()["detail"]["type"] == "backend_timeout"


def test_backend_failure_maps_to_controlled_502(fake_backend: FakeBackend):
    fake_backend.error = gateway.BackendFailure("simulated failure")
    client = TestClient(gateway.create_gateway_app(fake_backend))

    response = client.post("/v1/chat/completions", json=payload())

    assert response.status_code == 502
    assert response.json()["detail"]["type"] == "backend_failure"


def test_stream_relays_ordered_chunks_and_done(client: TestClient, fake_backend: FakeBackend):
    response = client.post("/v1/chat/completions", json=payload(stream=True))

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    events = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    chunks = [json.loads(event)["choices"][0]["delta"]["content"] for event in events[:-1]]
    assert chunks == ["C", "aching"]
    assert events[-1] == "[DONE]"
    assert fake_backend.calls[0].max_new_tokens == 16


def test_invalid_payload_is_rejected_before_backend(client: TestClient, fake_backend: FakeBackend):
    response = client.post("/v1/chat/completions", json={"model": "local-qwen", "messages": []})

    assert response.status_code == 422
    assert fake_backend.calls == []


def test_metrics_include_successful_request(client: TestClient):
    client.post("/v1/chat/completions", json=payload())

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "gateway_requests_total" in metrics.text
    assert 'gateway_requests_total{mode="non_stream",outcome="success"} 1.0' in metrics.text
