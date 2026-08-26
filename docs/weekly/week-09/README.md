# Week 09 - Distributed Benchmarking

## Read

- HLSO: Chapter 4, `Latency Metrics`, `Throughput Metrics`, `Best Practices for Performance Measurement`, and `Continuously monitor performance in production`; revisit Chapter 9 `Step 3: Define Evaluation Metrics`.
- DAS: Chapter 10, `Percentile latencies`, `Efficiency metrics`, `Benchmarking methodology`, `Inference benchmarking`, `Cold start vs warm performance`, and `Validating inference accuracy`.
- AISPE PDF: Chapter 15, pages 663-699; Chapter 16, pages 701-758. Focus on parallelism, routing, batching, monitoring, quantization, and fault handling.

## Do

Run interactive-chat, long-context-prefill, and throughput-batch workloads at concurrency 1, 4, 16, and 32 where hardware allows. Add a 30-minute soak and one injected failure.

## Output

Raw JSON/CSV, environment capture, p50/p95/p99 plots, TTFT/TPOT/throughput report, error budget, quality results, and scaling-efficiency calculation.

## Course alignment

Course Weeks 2-3 and 8-9: benchmarking, observability, and scale decisions.

