# Week 06 - Profile, Tune, and Repeat

## Mini-project: choose serving profiles

Turn the experiment matrix into three reproducible configurations: balanced, latency-first, and throughput-first.

## Read

- HLSO: Chapter 9, `LLM Serving Optimization Plan`, all eight `Optimize Qwen3-14B serving with vLLM` steps, and `Common Optimization Trade-offs`.
- DAS: Chapter 10, `Benchmarking fundamentals`, `Understanding percentile latencies`, `Efficiency metrics`, `Benchmarking methodology`, `Inference benchmarking`, and `Validating inference accuracy`.
- AISPE PDF: Chapter 16, pages 701-758; focus on Nsight profiling, batching/scheduling, KV-cache memory, quantization, prompt compression, prefix caching, streaming, and timeouts.

## Do

Run the fixed matrix for concurrency, prompt/output length, quantization, chunked prefill, prefix caching, and GPU-memory utilization. Use Prometheus plus one profiler trace to explain results.

## Test today

Start with a small matrix: concurrency 1/4/16, short/long prompts, short/long outputs, and the candidate settings from Week 4. Change one setting at a time, then repeat the best combinations. Capture request-level results and server-level metrics in the same time window.

Rank configurations separately for interactive latency and throughput. Select three profiles: `latency` minimizes TTFT/tail latency, `throughput` maximizes output tokens per second, and `balanced` meets both a latency and quality target. Include memory headroom and failure rate in the decision.

## Output

Ranked configuration table with `balanced`, `latency`, and `throughput` profiles, each backed by quality and performance data.

## Done when

- [ ] The matrix and exact launch flags are saved.
- [ ] Prometheus metrics and one profiler trace are linked to conclusions.
- [ ] p50 and p95/p99 are reported, not only averages.
- [ ] Three profiles are selected with explicit workload assumptions.

## Course alignment

Course Weeks 3-5: profiling tools, optimization, and hardware/model choice.
