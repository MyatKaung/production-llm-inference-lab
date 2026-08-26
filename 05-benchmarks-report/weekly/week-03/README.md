# Week 03 - Hardware Budget and Baseline Profile

## Read

- HLSO: Chapter 5, `Reading GPU specs`, `Estimating Model Size`, `Estimating KV Cache Size`, `Boundaries of GPU Compute and Memory Bandwidth`, and `Applying Arithmetic Intensity Analysis to the LLM Prefill and Decode Phases`.
- DAS: Chapter 2, `Key metrics for AI clusters`, `GPU`, `Choosing the right GPU`, `Architecture features that matter`, and `Multinode communication`.
- AISPE PDF: Chapter 2, pages 23-53; Chapter 3, pages 55-101. Focus on GPU monitoring, CPU/GPU interaction, NUMA, container runtime, Kubernetes resource guarantees, and OOM handling.

## Do

Profile prompt lengths 128, 1K, and 4K at concurrency 1, 4, and 16. Separate queue, prefill, decode, and client/network time. Create a fixed evaluation set with deterministic scoring before quantization.

## Output

Hardware/model feasibility sheet, baseline bottleneck report, evaluation set, scorer, and baseline quality score.

## Course alignment

Course Weeks 1-3: hardware, request-to-token reasoning, and profiling.

