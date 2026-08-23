# Week 0 Hardware and Budget Decision

Complete and commit this document before renting compute.

## Local baseline

- Mac model / chip: MacBook Pro (Mac15,6) / Apple M3 Pro, 11 CPU cores
- RAM: 18 GB unified memory
- local runtime: Hugging Face or MLX baseline; evaluate vLLM-Metal only as a smoke-test path
- smallest instruct model:
- local model dtype:
- measured tokens per second:
- vLLM-Metal smoke-test decision: pending Week 0 measurement; it does not replace the NVIDIA/CUDA experiments

## Cloud plan

- provider:
- region:
- GPU class and VRAM:
- GPU count:
- image / CUDA / driver versions:
- storage size and retention:
- hourly compute price at booking time:
- expected hours by roadmap week:
- hard project spend cap:
- per-session spend limit:

## Shutdown discipline

- automatic idle timeout:
- maximum session duration:
- process that terminates instances after a benchmark:
- volume and snapshot cleanup rule:
- daily cost-alert threshold:

## Cost calculation

```text
run_cost = instance_hourly_price * billed_hours + storage + egress
cost_per_1m_output_tokens = run_cost / measured_output_tokens * 1_000_000
```

Record warmup and failed-run costs separately. Do not hide them from the final project cost.

## Decision

- selected plan:
- rejected alternatives:
- reason:
- date checked:
