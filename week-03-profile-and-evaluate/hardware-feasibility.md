# Week 3 hardware and model feasibility

This is a planning worksheet, not a promise that a model will load. Weight memory is only one part of inference memory. Leave headroom for the KV cache, temporary activations, runtime allocations, and fragmentation.

## Current baseline

| Item | Current choice | Record your observation |
|---|---|---|
| Local hardware | Apple Silicon Mac with 18 GB unified memory | |
| Baseline model | Qwen 2.5 0.5B Instruct | |
| Local runtime | PyTorch MPS | |
| CUDA machine | Remote NVIDIA GPU available for later CUDA work | GPU model and usable memory: |
| Baseline device | MPS | |

## First-pass weight-memory estimate

For an FP16/BF16 model:

```text
weight memory ≈ parameter count × 2 bytes
```

| Candidate model size | FP16/BF16 weights only | Why this is not enough | Initial decision |
|---:|---:|---|---|
| 0.5B | about 1 GB | still needs runtime/KV headroom | current baseline |
| 3B | about 6 GB | add KV cache and runtime memory | reasonable candidate |
| 7B | about 14 GB | very little room remains on 18 GB unified memory | test carefully or use CUDA |
| 14B | about 28 GB | exceeds local unified memory before KV cache | use suitable CUDA GPU |

## What to measure before changing model

- Model load succeeds or fails, and why.
- Device-reported memory before and after model load.
- Prompt length, output limit, and concurrency used.
- Whether the 4K / concurrency-16 pressure case produces repeated errors or makes the machine unresponsive.

## Decision rule

Do not choose a larger model because its weight estimate barely fits. First reserve headroom, then run a small smoke test, then run the same Week 3 quality gate and benchmark workload. If the system cannot complete the workload reliably, it is not a feasible serving configuration.
