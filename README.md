# Production LLM Inference Lab

A portfolio project for learning production LLM inference by building one system, measuring it, and improving it with evidence.

## Target system

```text
Client
  -> OpenAI-compatible inference gateway
  -> request queue / routing / admission control
  -> vLLM or SGLang model server
  -> GPU

Metrics -> Prometheus -> Grafana
Traces  -> OpenTelemetry
Tests   -> benchmark runner -> reproducible reports
```

The final system supports streaming and non-streaming responses, configurable backends, request limits, production metrics, Kubernetes deployment, and repeatable performance experiments.

## Five implementation work areas

| Folder | Responsibility | Main output |
| --- | --- | --- |
| `01-baseline-serving` | Establish the simplest correct server and request-to-token mental model | Hugging Face baseline and measurements |
| `02-inference-gateway` | Own the public API, streaming, routing, limits, and telemetry | OpenAI-compatible gateway |
| `03-optimization-lab` | Run controlled vLLM/SGLang optimization experiments | Experiment configs and result tables |
| `04-distributed-serving` | Package and operate the system on Kubernetes | Manifests, scaling tests, and runbooks |
| `05-benchmarks-report` | Keep workloads, raw results, plots, and conclusions reproducible | Final engineering report |

The weekly curriculum is navigation/documentation, not a sixth implementation area. It lives in [`docs/weekly`](docs/weekly/README.md). The five folders above are where the actual system and its evidence belong.

## Success criteria

- One command starts the local baseline.
- The same client works against Hugging Face, vLLM, and SGLang backends.
- Both streaming and non-streaming endpoints are tested.
- Every optimization has before/after data; no unsupported "faster" claims.
- Every optimization report includes a quality delta from the fixed evaluation set.
- Reports include TTFT, TPOT, inter-token latency, end-to-end latency, throughput, GPU memory, GPU utilization, queue time, error rate, and cost assumptions.
- Kubernetes deployment includes readiness, liveness, resource limits, graceful shutdown, metrics, and a rollback procedure.
- A new engineer can reproduce the chosen benchmark from the README.

## Model sizing rule

Use a model that fits the hardware and preserves the experiment. Start with a 0.5B-3B instruct model locally, use 7B-14B when a suitable GPU is available, and attempt 70B only when multi-GPU capacity is explicitly available. The project evaluates engineering decisions; it does not require pretending to run a 405B model.

Complete [WEEK-0-HARDWARE-BUDGET.md](WEEK-0-HARDWARE-BUDGET.md), then use the [weekly reading guides](docs/weekly/README.md) alongside [ROADMAP.md](ROADMAP.md). [OUTSOURCE_SPEC.md](OUTSOURCE_SPEC.md) strictly limits outside help to mechanical chores so the portfolio remains defensible.
