# Week 03 - Hardware Budget and Baseline Profile

## Mini-project: create the measurement and quality gate

Build the benchmark input set, deterministic quality scorer, hardware feasibility sheet, and baseline profile that every later optimization must pass.

## Read

- HLSO: Chapter 5, `Reading GPU specs`, `Estimating Model Size`, `Estimating KV Cache Size`, `Boundaries of GPU Compute and Memory Bandwidth`, and `Applying Arithmetic Intensity Analysis to the LLM Prefill and Decode Phases`.
- DAS: Chapter 2, `Key metrics for AI clusters`, `GPU`, `Choosing the right GPU`, `Architecture features that matter`, and `Multinode communication`.
- AISPE PDF: Chapter 2, pages 23-53; Chapter 3, pages 55-101. Focus on GPU monitoring, CPU/GPU interaction, NUMA, container runtime, Kubernetes resource guarantees, and OOM handling.

## Do

Profile prompt lengths 128, 1K, and 4K at concurrency 1, 4, and 16. Separate queue, prefill, decode, and client/network time. Create a fixed evaluation set with deterministic scoring before quantization.

## Test today

Create a matrix with one row per `(prompt_length, concurrency)` pair. Warm up every condition, keep model and generation parameters fixed, and collect enough samples for p50/p95. Check that total time approximately decomposes into queue + prefill + decode + transport.

Create 10-20 evaluation prompts covering instruction following, extraction, summarization, and refusal/safety behavior relevant to this lab. Save expected properties and a deterministic scorer. Run the baseline twice to confirm the score is repeatable. Treat this score as a quality gate for every later optimization.

Classify each condition as compute-bound, memory-bandwidth-bound, or queue-bound and support the classification with utilization, latency, or scaling evidence.

## Output

Hardware/model feasibility sheet, baseline bottleneck report, evaluation set, scorer, and baseline quality score.

## Done when

- [ ] All nine profile cells have raw machine-readable data.
- [ ] Queue, prefill, decode, and client time are separated or explicitly marked unavailable.
- [ ] Baseline quality scoring is repeatable.
- [ ] A written bottleneck hypothesis is supported by measurements.

## Course alignment

Course Weeks 1-3: hardware, request-to-token reasoning, and profiling.
