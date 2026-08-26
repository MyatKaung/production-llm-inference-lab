# Week 04 - Essential Optimizations

## Mini-project: prove three optimization effects

Run controlled experiments for batching, quantization, and prefix caching. The deliverable is evidence, not a collection of flags.

## Read

- HLSO: Chapter 6, `Dynamic Batching`, `Continuous Batching`, `Continuous Batching with Chunked Prefill`, `FlashAttention`, `PagedAttention`, `Quantization`, `Hands-on quantization`, `Running benchmarks`, and `Prefix Caching`.
- DAS: Chapter 6, `KV cache`, `PagedAttention`, and `The decode phase and its inefficiencies`.
- AISPE PDF: Chapter 16, pages 701-758; focus on `Dynamic Batching`, `Continuous Batching`, `Stall-Free Scheduling (Chunked Prefill)`, `Quantization Approaches for Real-Time Inference`, and `Prefix Caching`.

## Do

In `03-optimization-lab`, run one-factor-at-a-time experiments for continuous batching, one quantized model, and prefix caching. Keep workload, model, hardware, warmup, and measurement window fixed.

## Output

Three experiment manifests, raw results, quality deltas, and a decision table for latency, throughput, memory, and quality.

## Course alignment

Course Weeks 3-4: profiling and step-by-step optimization.
