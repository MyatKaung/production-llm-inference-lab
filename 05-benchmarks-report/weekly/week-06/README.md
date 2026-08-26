# Week 06 - Profile, Tune, and Repeat

## Read

- HLSO: Chapter 9, `LLM Serving Optimization Plan`, all eight `Optimize Qwen3-14B serving with vLLM` steps, and `Common Optimization Trade-offs`.
- DAS: Chapter 10, `Benchmarking fundamentals`, `Understanding percentile latencies`, `Efficiency metrics`, `Benchmarking methodology`, `Inference benchmarking`, and `Validating inference accuracy`.
- AISPE PDF: Chapter 16, pages 701-758; focus on Nsight profiling, batching/scheduling, KV-cache memory, quantization, prompt compression, prefix caching, streaming, and timeouts.

## Do

Run the fixed matrix for concurrency, prompt/output length, quantization, chunked prefill, prefix caching, and GPU-memory utilization. Use Prometheus plus one profiler trace to explain results.

## Output

Ranked configuration table with `balanced`, `latency`, and `throughput` profiles, each backed by quality and performance data.

## Course alignment

Course Weeks 3-5: profiling tools, optimization, and hardware/model choice.

