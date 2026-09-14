# Week 03 - Hardware Budget and Baseline Profile

## Mini-project: create the measurement and quality gate

Build the benchmark input set, deterministic quality scorer, hardware feasibility sheet, and baseline profile that every later optimization must pass.

## Read

- HLSO: Chapter 5, `Reading GPU specs`, `Estimating Model Size`, `Estimating KV Cache Size`, `Boundaries of GPU Compute and Memory Bandwidth`, and `Applying Arithmetic Intensity Analysis to the LLM Prefill and Decode Phases`.
- DAS: Chapter 2, `Key metrics for AI clusters`, `GPU`, `Choosing the right GPU`, `Architecture features that matter`, and `Multinode communication`.
- AISPE PDF: Chapter 2, pages 23-53; Chapter 3, pages 55-101. Focus on GPU monitoring, CPU/GPU interaction, NUMA, container runtime, Kubernetes resource guarantees, and OOM handling.

## Do

Profile prompt lengths 128, 1K, and 4K at concurrency 1, 4, and 16 through the public gateway. Separate queue, prefill, decode, and client/network time. Create a fixed evaluation set with deterministic scoring before quantization. Add one controlled long-prompt/high-concurrency pressure case and document the first observed system limit.

## Test today

Create a matrix with one row per `(prompt_length, concurrency)` pair. Warm up every condition, keep model and generation parameters fixed, and collect enough samples for p50/p95. Check that total time approximately decomposes into queue + prefill + decode + transport.

Create 10-20 evaluation prompts covering instruction following, extraction, summarization, and refusal/safety behavior relevant to this lab. Save expected properties and a deterministic scorer. Run the baseline twice to confirm the score is repeatable. Treat this score as a quality gate for every later optimization.

Classify each condition as compute-bound, memory-bandwidth-bound, or queue-bound and support the classification with utilization, latency, or scaling evidence.

For the pressure case, record successful and failed requests, p50/p95 TTFT and total latency, gateway in-flight/error metrics, and any observed memory pressure. Stop if the machine becomes unresponsive or errors repeat; the purpose is to find the boundary, not to force a crash.

## Run today

Start the Week 01 model server on port `8001`, then the Week 02 gateway on port `8000`. The Week 3 tools call only the public gateway.

Run the fixed quality set twice. The second run verifies that every case has the same pass/fail outcome as the first:

```bash
uv run --python .venv/bin/python week-03-profile-and-evaluate/quality_gate.py \
  --label baseline-run-1

uv run --python .venv/bin/python week-03-profile-and-evaluate/quality_gate.py \
  --label baseline-run-2 \
  --compare-with week-03-profile-and-evaluate/results/quality-baseline-run-1.json
```

First smoke-test one short streaming wave:

```bash
uv run --python .venv/bin/python week-03-profile-and-evaluate/benchmark_client.py \
  --mode matrix --prompt-lengths 128 --concurrencies 1 \
  --warmup-waves 1 --measured-waves 1 --max-tokens 16 --label smoke
```

Then run the matrix. A wave contains the configured number of simultaneous requests, so ten measured waves at concurrency 16 create 160 measured request records for that cell. The client completes every concurrency-1 cell first, then stops after the first failed concurrent wave by default. This preserves valid evidence and avoids repeatedly hitting a crashed backend:

```bash
uv run --python .venv/bin/python week-03-profile-and-evaluate/benchmark_client.py \
  --mode matrix --label baseline
```

Use `--continue-after-failure` only when you have confirmed that the backend remains healthy after the failure. It is intentionally not the default.

Run the pressure case only after the matrix has completed:

```bash
uv run --python .venv/bin/python week-03-profile-and-evaluate/benchmark_client.py \
  --mode pressure --label pressure-4k-c16
```

The guided version of this sequence is [`01-quality-gate-and-gateway-profile.ipynb`](01-quality-gate-and-gateway-profile.ipynb). It keeps the full matrix and pressure case disabled until you explicitly enable them.

## Output

Hardware/model feasibility sheet, baseline bottleneck report, evaluation set, scorer, quality-run artifacts, raw benchmark rows, and gateway-metrics artifacts.

## Done when

- [ ] All nine profile cells have raw machine-readable data.
- [ ] Queue, prefill, decode, and client time are separated or explicitly marked unavailable.
- [ ] Baseline quality scoring is repeatable.
- [ ] A written bottleneck hypothesis is supported by measurements.
- [ ] The controlled pressure case has an honest success/error and tail-latency record.

## Course alignment

Course Weeks 1-3: hardware, request-to-token reasoning, and profiling.
