# Week 04 - Essential Optimizations

## Mini-project: prove three optimization effects

Run controlled experiments for batching, quantization, and prefix caching. The deliverable is evidence, not a collection of flags.

## Read

- HLSO: Chapter 6, `Dynamic Batching`, `Continuous Batching`, `Continuous Batching with Chunked Prefill`, `FlashAttention`, `PagedAttention`, `Quantization`, `Hands-on quantization`, `Running benchmarks`, and `Prefix Caching`.
- DAS: Chapter 6, `KV cache`, `PagedAttention`, and `The decode phase and its inefficiencies`.
- AISPE PDF: Chapter 16, pages 701-758; focus on `Dynamic Batching`, `Continuous Batching`, `Stall-Free Scheduling (Chunked Prefill)`, `Quantization Approaches for Real-Time Inference`, and `Prefix Caching`.

## Do

In `03-optimization-lab`, run one-factor-at-a-time experiments for continuous batching, one quantized model, and prefix caching. Keep workload, model, hardware, warmup, and measurement window fixed.

## Test today

Create three manifests. Each manifest must state the baseline, one changed factor, workload, seed/generation settings, warm-up count, sample count, hardware, and quality threshold.

Test batching at concurrency 1, 4, and 16; one quantized variant against the same prompts; and repeated-prefix versus unique-prefix traffic. Compare TTFT, ITL/TPOT, end-to-end latency, throughput, peak memory, and quality score. Run each experiment more than once and keep raw results.

An optimization wins only if its improvement matters for the stated workload and its quality delta stays inside the Week 3 gate. If it helps one condition and hurts another, record the boundary instead of averaging it away.

## Output

Three experiment manifests, raw results, quality deltas, and a decision table for latency, throughput, memory, and quality.

## Done when

- [ ] Exactly one primary variable changes per experiment.
- [ ] Warm-up and measurement windows are documented.
- [ ] Every result has a quality delta.
- [ ] The decision table says `adopt`, `reject`, or `keep for a specific workload`.

## Course alignment

Course Weeks 3-4: profiling and step-by-step optimization.
