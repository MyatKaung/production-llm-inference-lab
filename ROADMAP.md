# Ten-Week Roadmap

Use only these three books:

1. *Hands-On LLM Serving and Optimization* (HLSO)
2. *Distributed AI Systems* (DAS)
3. *AI Systems Performance Engineering* (AISPE)

All references use chapter and section names so they are followable in both EPUB and PDF editions.

## Week 0 - Hardware and Budget Preflight

Complete this before starting the ten-week clock. Use [WEEK-0-HARDWARE-BUDGET.md](WEEK-0-HARDWARE-BUDGET.md) to record:

- local Mac capabilities and the smallest model that runs correctly;
- whether vLLM-Metal is useful for local smoke tests;
- the cloud provider and GPU class for CUDA-specific vLLM/SGLang work;
- a hard project spend cap and per-session spend limit;
- automatic idle shutdown and volume/snapshot cleanup rules;
- the cost-per-million-output-tokens formula used in later reports.

Do not rent a GPU until the workload, commands, expected runtime, and stop condition are written down.

## Week 1 - Request to Token Baseline

**Read**

- HLSO Chapter 2: `Executing LLM Generation`, `KV Cache`, `Prefill and Decode`, `Streaming`, and `Batch Serving`.
- HLSO Chapter 4: `Measuring Performance in LLM Serving`, including latency metrics, throughput metrics, TTFT/ITL decomposition, realistic traffic, experiment consistency, and avoiding inflated results.
- AISPE Chapter 1: `The AI Systems Performance Engineer`, `Benchmarking and Profiling`, `Measuring Goodput`, and `Transparency and Reproducibility`.

**Build**

- In `01-baseline-serving`, run one small instruct model with Hugging Face Transformers.
- Expose one non-streaming endpoint and one streaming endpoint.
- Record model parameters, dtype, weight memory estimate, KV-cache estimate, prompt tokens, output tokens, TTFT, and total latency.

**Commit evidence**

- Architecture note, model-memory calculator, launch command, and `baseline.json` result.

## Week 2 - Inference Gateway

**Read**

- HLSO Chapter 3: `Build an Online LLM Serving Service from Scratch`, batching, streaming with batching, and the general single-model design.

**Build**

- In `02-inference-gateway`, implement `/v1/chat/completions` with OpenAI-compatible request and response shapes.
- Add streaming, request IDs, timeouts, cancellation, maximum input/output tokens, and backend selection.
- Keep the model server behind the gateway; clients must not call it directly.

**Commit evidence**

- API contract tests and a sequence diagram for request, prefill, decode, stream, and cancellation.

## Week 3 - Hardware Budget and Baseline Profile

**Read**

- HLSO Chapter 5: GPU specifications, model loading, model-size and KV-cache estimates, compute-versus-memory bottlenecks, and arithmetic intensity in prefill/decode.
- AISPE Chapter 2: `Performance Monitoring and Utilization in Practice`, `Sharing and Scheduling`, and the CPU/GPU/interconnect sections needed for the selected hardware.
- AISPE Chapter 3: focus on `NUMA Awareness and CPU Pinning`, GPU runtime settings, container runtime optimization, Kubernetes resource guarantees, and OOM behavior.

**Build**

- Create a hardware/model feasibility sheet for 3B, 7B, and 14B models.
- Profile the Week 1 baseline under prompt lengths 128, 1K, and 4K and concurrency 1, 4, and 16.
- Separate queue time, prefill time, decode time, and client/network overhead.
- Add a fixed evaluation set and deterministic scoring script before running any quantization experiment. Record the baseline score and treat it as a quality gate.

**Commit evidence**

- Hardware decision record and a baseline bottleneck report. State whether each workload is compute-, memory-, or queue-bound and why.

## Week 4 - Essential Optimizations

**Read**

- HLSO Chapter 6: dynamic and continuous batching, chunked prefill, FlashAttention, PagedAttention, quantization, prefix caching, and RadixAttention.

**Build**

- In `03-optimization-lab`, run controlled experiments for batching, one quantized model, and prefix caching.
- Change one factor per experiment. Keep model, workload, hardware, warmup, and measurement window fixed.

**Commit evidence**

- Three experiment manifests, raw results, and a decision table showing measured quality delta, latency, throughput, and memory tradeoffs. An optimization cannot win if its quality delta is missing.

## Week 5 - vLLM Internals and Serving

**Read**

- HLSO Chapter 8: vLLM architecture, EngineCore, scheduler, ModelExecutor, request workflow, and layered optimization strategy.
- DAS Chapter 6: vLLM setup, KV cache, PagedAttention, TP/DP/PP, chunked prefill, OpenAI-compatible API, and throughput benchmarking.

**Build**

- Serve the selected model with vLLM and route the Week 2 gateway to it.
- Compare Hugging Face and vLLM using the identical benchmark workload.
- Capture scheduler settings, GPU-memory utilization, maximum sequence length, batching behavior, and failure limits.

**Commit evidence**

- Reproducible vLLM launch config and a baseline-versus-vLLM report.

## Week 6 - Profile, Tune, Repeat

**Read**

- HLSO Chapter 9: the complete Qwen optimization workflow and common tradeoffs.
- AISPE Chapter 16: `Monitoring System Metrics and Counters`, `Profiling with Nsight Systems and Nsight Compute`, `Dynamic Batching, Scheduling, and Routing`, `Quantization Approaches for Real-Time Inference`, and the application-level optimization sections on prefix caching, streaming, limits, and timeouts.

**Build**

- Tune vLLM with a fixed experiment matrix: concurrency, prompt/output length, quantization, chunked prefill, prefix caching, and GPU-memory utilization.
- Use Prometheus metrics plus one profiler trace to explain the best and worst run.

**Commit evidence**

- Ranked configuration table. Choose one `balanced`, one `latency`, and one `throughput` profile with measured reasons.

## Week 7 - SGLang and Distributed Strategies

**Read**

- HLSO Chapter 7: speculative decoding, multi-GPU inference, TP/PP/DP/EP, prefill-decode disaggregation, KV-cache transfer, and self-hosting tradeoffs.
- DAS Chapter 7: SGLang architecture, RadixAttention, router policies, session affinity, fault tolerance, and production deployment patterns.

**Build**

- Add SGLang as the second optimized backend.
- Compare prefix-heavy multi-turn traffic against vLLM.
- Run one speculative-decoding before/after experiment using the same workload and quality gate.
- If two GPUs are available, test one parallelism strategy. Otherwise, produce the deployment design and validate routing/failure behavior with multiple small replicas.

**Commit evidence**

- Framework selection ADR, plus speculative-decoding raw results and a decision on when it helps or hurts.

## Week 8 - Production Kubernetes Stack

**Read**

- DAS Chapter 9: routing, load balancing, canary deployment, observability, reliability, cost, Kubernetes, multi-model/multi-engine serving, and llm-d.
- HLSO Chapter 4: `LLM Serving in Enterprise Systems`, the seven serving layers, `Building with an Open Source Stack`, and `Build or Buy? Understanding Strategies`.
- Revisit AISPE Chapter 3: `Container Runtime Optimizations for GPUs` and the Kubernetes sections on topology management, scheduling, network communication, orchestration jitter, resource guarantees, OOM, and I/O isolation.

**Build**

- In `04-distributed-serving`, deploy gateway, model server, Prometheus instrumentation, and OpenTelemetry traces to a single-node production-like Kubernetes environment.
- Add readiness/liveness probes, graceful shutdown, rate limiting, resource requests/limits, and a canary rollout/rollback procedure.
- Treat multi-node Kubernetes and production autoscaling as a documented design unless the hardware budget and Week 6 data justify deploying them.

**Commit evidence**

- Kubernetes manifests or Helm chart, dashboard screenshots, failure test notes, and an operator runbook.

## Week 9 - Distributed Benchmarking

**Read**

- DAS Chapter 10: percentile latency, efficiency metrics, benchmark methodology, inference tools, cold-versus-warm behavior, and accuracy validation.
- AISPE Chapter 15: `Disaggregated Prefill and Decode Architecture`, `Parallelism Strategies for Serving Massive MoE Models`, speculative decoding, constrained-decoding performance, dynamic routing, and load balancing.

**Build**

- In `05-benchmarks-report`, define three workloads: interactive chat, long-context prefill, and throughput batch.
- Test concurrency 1, 4, 16, and 32 where hardware allows.
- Add a 30-minute soak test and one injected failure: backend termination, OOM, timeout, or overloaded queue.

**Commit evidence**

- Raw machine-readable results, exact commands/configs, plots, p50/p95/p99 analysis, error budget, and a scaling-efficiency calculation.

## Week 10 - Advanced Decision and Final Report

**Read selectively**

- AISPE Chapter 17: `Why Prefill-Decode Disaggregation?`, disaggregated cluster pools, routing/scheduling policies, and scalability.
- AISPE Chapter 18: `Tuning KV Cache Utilization and Management`, KV-cache transfer, `SLO-Aware Request Management and Fault Tolerance`, and dynamic scheduling/load balancing.
- AISPE Chapter 19: read only adaptive batching, chunked prefill, KV-cache policy switching, and topology-aware scheduling.
- AISPE Appendix A: the inference/serving, profiling/monitoring, and reproducibility checklist sections.

**Build**

- Choose one advanced feature justified by Week 9 data: constrained decoding, multi-LoRA serving, semantic caching, or prefill/decode disaggregation. Do not implement a feature merely because it appears in a book.
- Run the final before/after benchmark and write the production recommendation.
- Polish setup instructions, architecture, runbook, known limits, and future-work boundaries.
- Audit the project with AISPE Appendix A and mark relevant items `done`, `not applicable`, or `deliberately skipped` with a reason.

**Commit evidence**

- Final report, architecture decision records, one-command reproduction path, and a short portfolio demo.

## Weekly operating rule

Every week ends with this chain:

```text
hypothesis -> fixed workload -> baseline -> one change -> measurement -> conclusion -> commit
```

Do not count reading as completed until its idea appears in code, configuration, a benchmark, or an explicit decision record.

Spend 45 minutes each week reading the official release notes and documentation for the exact vLLM, SGLang, Kubernetes, and profiling-tool versions pinned that week. Record book/documentation conflicts in `PRIMARY-SOURCE-LOG.md`.
