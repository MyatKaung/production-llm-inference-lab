# Week 3 bottleneck report

Complete this after the quality gate, matrix, and pressure case. State measurements separately from conclusions.

## Experiment identity

| Field | Value |
|---|---|
| Date | 15 September 2026 |
| Model and revision | Qwen 2.5 0.5B Instruct (local cached model) |
| Device and runtime | Apple Silicon MPS through PyTorch/Transformers |
| Gateway URL | local Week 2 public gateway |
| Generation settings | greedy, fixed 64-token output limit |
| Quality baseline run 1 | 7 / 10 passed |
| Quality baseline run 2 | 7 / 10 passed |
| Repeatable result? | Yes: the same per-case pass/fail outcomes |

## Matrix summary

Copy p50/p95 values from the generated result artifacts. Do not use a missing number as zero.

| Prompt target | Actual prompt tokens | Concurrency | Success / total | TTFT p50 / p95 | Total p50 / p95 | Observation |
|---:|---:|---:|---:|---:|---:|---|
| 128 | 127 | 1 | 10 / 10 | 0.134 / 0.145 s | 0.242 / 0.273 s | valid baseline |
| 128 | 127 | 4 | not continued | unavailable | unavailable | concurrent MPS run had already crashed the backend in the first discovery run |
| 128 | 127 | 16 | not continued | unavailable | unavailable | no repeated crash attempts after the safe-stop policy |
| 1K | 1,022 | 1 | 10 / 10 | 0.409 / 0.415 s | 0.502 / 0.522 s | valid baseline |
| 1K | 1,022 | 4 | not continued | unavailable | unavailable | no repeated crash attempts after the safe-stop policy |
| 1K | 1,022 | 16 | not continued | unavailable | unavailable | no repeated crash attempts after the safe-stop policy |
| 4K | 4,097 | 1 | 10 / 10 | 1.701 / 1.772 s | 1.921 / 1.998 s | valid baseline; TTFT rises strongly with prompt length |
| 4K | 4,097 | 4 | not continued | unavailable | unavailable | no repeated crash attempts after the safe-stop policy |
| 4K | 4,097 | 16 | 0 / 16 | unavailable | unavailable | controlled pressure case caused a backend failure for every request |

## Controlled pressure case

| Item | Result |
|---|---|
| Prompt target / concurrency | 4K / 16 |
| Successful requests | 0 / 16 |
| Failed requests | 16 / 16 |
| TTFT p95 | unavailable: no request produced a streamed token |
| Total-latency p95 | unavailable: no request reached `[DONE]` |
| Peak gateway in-flight requests | 16 |
| Backend-error metric change | 776 to 792 after gateway cleanup (+16) |
| Memory-pressure observation | the Week 1 MPS model-server process exited during the 4K/concurrency-16 wave |
| Stop condition reached? | Yes: a measured wave had failures, so the client stopped immediately |

## Time decomposition

| Component | What we know |
|---|---|
| Queue time | **Unavailable** in the current gateway: it has no explicit admission queue timer. |
| Client-observed TTFT | Measured by the benchmark client; includes client, gateway, backend, prefill, and first-stream-delivery overhead. |
| Prefill | Inferred from prompt-length effects on TTFT; not an isolated internal timer yet. |
| Decode / ITL | Requires per-chunk timing analysis; Week 1 has token timing, but the public Week 2 stream currently does not expose final token usage. |
| Total latency | Measured by the benchmark client until `[DONE]`. |

## Bottleneck conclusion

Write one evidence-backed sentence for each relevant workload.

- Short prompt / low concurrency: the 127-token workload is healthy on MPS; p95 client-observed TTFT is 0.145 s.
- Long prompt / low concurrency: the 4,097-token workload is healthy but has p95 TTFT of 1.772 s, about 12 times the short-prompt result. Prefill is the likely dominant additional cost.
- High concurrency: no stable MPS concurrency result is available. The first discovery run crashed during a short-prompt concurrency-4 wave, so later cells were not treated as valid measurements.
- Pressure case: 4K/concurrency-16 crashed the model-server process and all 16 public requests failed. The current unbounded Transformer/MPS backend is not a feasible concurrent-serving configuration.

## Next decision

Do not try quantization next: it will not solve the missing concurrency control. First add explicit admission control or serialization for the MPS backend, then rerun the fixed quality gate and the same workload. Use the remote NVIDIA machine later for an actual batching/vLLM concurrency experiment.
