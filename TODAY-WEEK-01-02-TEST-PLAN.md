# Today: Week 01 + Week 02 Test Plan

## Goal

By the end of today, one client should call an OpenAI-compatible gateway, the gateway should call a Hugging Face model server, and you should have baseline latency measurements plus passing contract and failure tests.

```text
client -> gateway :8000 -> Hugging Face server :8001 -> model
                         metrics/logs
```

## Model choice

Start with:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

Use the exact model ID above and record the downloaded revision in your results. It is the default because it is a 0.49B-parameter instruct model and its official model card documents Transformers usage with `apply_chat_template`.

If it is too slow or does not fit, do not change models halfway through the benchmark. Fix the environment first. If the Mac has ample memory and the smoke test is comfortable, a later comparison can use `Qwen/Qwen2.5-1.5B-Instruct`, but it is not required today.

## Read first — 45 minutes

1. Week 01 README: request-to-token flow, KV cache, prefill, decode, streaming, and batch serving.
2. Week 02 README: gateway boundary, SSE, IDs, limits, timeout, cancellation, and backend adapters.
3. [Qwen2.5-0.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct): model details and Transformers example.
4. [Hugging Face chat templates](https://huggingface.co/docs/transformers/chat_templating): why the tokenizer's chat template must be used.
5. Write this hypothesis before testing: “Warm latency is lower than cold latency; longer prompts mainly increase TTFT; longer outputs mainly increase decode time.”

## Phase A — Week 01 baseline server

### A1. Environment smoke test

Create a virtual environment and install the smallest required stack:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install torch transformers accelerate fastapi uvicorn sse-starlette httpx pytest
```

On Apple Silicon, use the MPS device when available; otherwise use CPU. Record Python, PyTorch, Transformers, device, OS, and model revision.

### A2. Model smoke test

Before adding HTTP, load the tokenizer and model and generate one answer using the tokenizer's chat template. Confirm:

- the model loads without an out-of-memory error;
- the answer is non-empty;
- prompt and output token counts are available;
- generation stops at an EOS/stop condition;
- the second request does not reload the model.

### A3. Server tests

Expose two internal endpoints:

```text
POST /generate              # complete JSON response
POST /generate/stream       # SSE token stream
GET  /health                # process/model health
```

Run these cases against the model server:

| Case | Expected result |
| --- | --- |
| Short prompt, `max_new_tokens=32` | 200, non-empty output |
| Same prompt, streaming | ordered SSE chunks and final completion event |
| Empty messages/input | 4xx validation error |
| `max_new_tokens=0` or over the limit | 4xx validation error |
| First request | succeeds; cold-start time recorded separately |
| Repeated request | succeeds without model reload |

### A4. Baseline measurement

Use three prompts:

```text
short:  "Explain caching in one sentence."
medium: "Explain how an HTTP request becomes generated tokens in 150 words."
long:   the medium prompt repeated enough to reach approximately 1,000 input tokens
```

For each prompt, run 1 warm-up and 5 measured requests with deterministic generation (`temperature=0` where supported, fixed seed if supported, fixed `max_new_tokens=64`). Record:

```text
model_id, model_revision, device, prompt_tokens, output_tokens,
cold_start_seconds, ttft_seconds, total_latency_seconds,
inter_token_latency_seconds, output_tokens_per_second, error
```

For streaming, define TTFT as time from request acceptance to the first token chunk. Define total latency as time to the final chunk. Report median and p95; do not report only the average.

## Phase B — Week 02 gateway

Put the gateway in front of the model server. The client must call only:

```text
http://localhost:8000/v1/chat/completions
```

The gateway translates the OpenAI-style request into the internal `/generate` contract and translates the response back. Add a generated request ID to logs and responses.

### B1. Contract tests — fake backend

Use a fake backend so these tests do not depend on model speed:

| Test | Expected result |
| --- | --- |
| Valid non-streaming chat request | OpenAI-shaped JSON response |
| Valid streaming request | ordered SSE chunks, final `[DONE]` |
| Missing/invalid `messages` | 4xx with structured error |
| Input token limit exceeded | 4xx; backend not called |
| Output token limit exceeded | 4xx; backend not called |
| Unknown backend | 4xx or 5xx according to your contract |
| Backend timeout | bounded 504-style error |
| Backend 5xx | mapped error with request ID |
| Client disconnect during stream | backend cancellation attempted |

### B2. Integration tests — real model server

Repeat one non-streaming and one streaming request through the gateway. Verify:

- the client never uses port 8001;
- the request ID appears in gateway logs;
- model output and token counts survive the translation;
- gateway latency is close to model-server latency plus a small overhead;
- timeout and cancellation do not leave an unbounded request running.

### B3. Minimal metrics

Expose `/metrics` on the gateway and record at least:

```text
requests_total{route,mode,status}
request_duration_seconds{route,mode}
request_tokens_total{direction}
in_flight_requests
backend_errors_total{backend}
```

## Acceptance gate for today

- [ ] Model loads and generates a response.
- [ ] Internal non-streaming and streaming endpoints pass.
- [ ] `baseline.json` contains 5 measured samples per prompt class.
- [ ] Median and p95 TTFT and total latency are reported.
- [ ] Gateway fake-backend contract tests pass.
- [ ] Gateway integration tests pass in both response modes.
- [ ] Invalid input, timeout, backend error, and cancellation are tested.
- [ ] A client calls only the gateway port.
- [ ] The exact launch commands and environment versions are written down.

## Stop conditions

Stop and record the failure instead of changing multiple variables if the model will not load, the server reloads the model on each request, streaming does not terminate, or cancellation cannot be observed. Those are debugging findings for today, not reasons to add batching, quantization, vLLM, or Kubernetes yet.

## Evidence to leave in the repository

```text
week-01-baseline-server/baseline.json
week-01-baseline-server/sequence-diagram.md
week-02-inference-gateway/tests/
week-02-inference-gateway/api-contract.md
today-environment.txt
```

## References

- [Week 01 README](week-01-baseline-server/README.md)
- [Week 02 README](week-02-inference-gateway/README.md)
- [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- [Transformers chat templates](https://huggingface.co/docs/transformers/chat_templating)
- [Transformers Apple Silicon/MPS guidance](https://huggingface.co/docs/transformers/en/perf_train_special)
