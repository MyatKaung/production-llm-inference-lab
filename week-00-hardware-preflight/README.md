# Week 00 - Hardware and Budget Preflight

## Mini-project: choose the lab hardware

Produce a one-page decision record that says what runs locally, what needs rented NVIDIA GPU time, and the maximum amount you will spend. This is a short prerequisite, not a performance week.

This is preparation, before the ten-week clock.

## Read

- HLSO: Chapter 1, `Why Optimize Model Serving`, `Single-Model Service`, and `Horizontal and vertical scaling`.
- DAS: Chapter 1, `Estimating model resource requirements`, `Inference memory requirements`, `GPU requirements estimation`, and `Decision framework: when do you need distributed systems?`.
- AISPE PDF: Chapter 1, pages 1-21; Chapter 2, pages 23-53. Focus on hardware/software codesign, GPU memory, interconnects, monitoring, and scheduling.

## Do

Complete `WEEK-0-HARDWARE-BUDGET.md`. Run a small local model on the Mac. Decide which CUDA experiments require rented NVIDIA GPU time.

## Test today

1. Record RAM, CPU/GPU type, available disk, and operating system.
2. Run a 0.5B-3B instruct model with a fixed prompt 3 times: cold start, warm non-streaming, and warm streaming.
3. Record whether it loads, peak memory, prompt/output token counts, and total time.
4. Estimate weight memory with `parameters × bytes_per_parameter`; add room for KV cache and runtime overhead.
5. Write the cloud GPU class, hourly cap, idle-shutdown rule, and an explicit stop condition before renting anything.

Do not optimize yet. The test is successful if you can explain exactly which experiment needs which hardware and what it will cost.

## Output

Commit the hardware decision, spend cap, shutdown rule, and cost-per-million-output-tokens formula.

## Done when

- [ ] A local smoke test result is recorded.
- [ ] 3B, 7B, and 14B feasibility is marked `fits`, `borderline`, or `does not fit`.
- [ ] The cost formula and maximum spend are written down.
- [ ] Every later CUDA experiment has a hardware and stop condition.

## Course alignment

Course Week 1: GPUs, hardware specs, and the physics/cost model of inference.
