# Week 09 - Distributed Benchmarking

## Mini-project: run the service under load

Run realistic traffic, a soak test, and one failure injection. Produce the first report that a platform engineer could use for capacity planning.

## Read

- HLSO: Chapter 4, `Latency Metrics`, `Throughput Metrics`, `Best Practices for Performance Measurement`, and `Continuously monitor performance in production`; revisit Chapter 9 `Step 3: Define Evaluation Metrics`.
- DAS: Chapter 10, `Percentile latencies`, `Efficiency metrics`, `Benchmarking methodology`, `Inference benchmarking`, `Cold start vs warm performance`, and `Validating inference accuracy`.
- AISPE PDF: Chapter 15, pages 663-699; Chapter 16, pages 701-758. Focus on parallelism, routing, batching, monitoring, quantization, and fault handling.

## Do

Run interactive-chat, long-context-prefill, and throughput-batch workloads at concurrency 1, 4, 16, and 32 where hardware allows. Add a 30-minute soak and one injected failure.

## Test today

Define the workload mix before running the test. For each workload, save the request generator version, model revision, prompt/output distributions, concurrency, warm-up, duration, and SLO. Run a small smoke load first, then the full matrix.

Report TTFT, TPOT/ITL, end-to-end latency, output-token throughput, queue time, GPU memory/utilization, error rate, and cost assumptions at p50/p95/p99. Run the soak test and inject one failure. Mark cold-start results separately from warm-service results.

Calculate scaling efficiency as measured throughput divided by ideal linear throughput, and explain any tail-latency or error-rate inflection. Do not call a configuration production-ready unless the quality gate and SLO both pass.

## Output

Raw JSON/CSV, environment capture, p50/p95/p99 plots, TTFT/TPOT/throughput report, error budget, quality results, and scaling-efficiency calculation.

## Done when

- [ ] Three workload definitions and exact commands are saved.
- [ ] The 30-minute soak completes or its failure is explained.
- [ ] One failure injection has an operator-facing result.
- [ ] Capacity and limits are stated from data, including uncertainty.

## Course alignment

Course Weeks 2-3 and 8-9: benchmarking, observability, and scale decisions.
