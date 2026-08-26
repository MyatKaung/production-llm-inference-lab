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

## Ten-week project structure

Each week is a small, reviewable project. You finish its README acceptance criteria and commit its artifact before moving to the next week.

| Week | Mini-project | Main output |
| --- | --- | --- |
| [00](week-00-hardware-preflight/README.md) | Hardware and budget preflight | Hardware decision record |
| [01](week-01-baseline-server/README.md) | Request-to-token baseline server | `baseline.json` |
| [02](week-02-inference-gateway/README.md) | OpenAI-compatible gateway | Gateway API and tests |
| [03](week-03-profile-and-evaluate/README.md) | Profile and quality gate | Evaluation set and bottleneck report |
| [04](week-04-batching-and-quantization/README.md) | Batching and quantization lab | Controlled experiment results |
| [05](week-05-vllm-server/README.md) | vLLM serving backend | HF-versus-vLLM report |
| [06](week-06-tune-and-benchmark/README.md) | Inference tuning matrix | Chosen serving profiles |
| [07](week-07-sglang-and-distributed/README.md) | SGLang and distributed serving | Framework ADR and speculative-decoding result |
| [08](week-08-kubernetes-serving/README.md) | Production-like Kubernetes service | Deployment and runbook |
| [09](week-09-load-test-and-report/README.md) | Load test and failure report | p50/p95/p99 report |
| [10](week-10-final-optimization/README.md) | Final optimization and design review | Portfolio-ready final report |

The original five work areas are distributed across these ten weekly projects. The repository is organized by week so the learning path and the code evidence stay together.

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

Start with [Week 00](week-00-hardware-preflight/README.md), use [ROADMAP.md](ROADMAP.md) for the complete mapping, and follow [OUTSOURCE_SPEC.md](OUTSOURCE_SPEC.md) for the strict boundary on outside help.
