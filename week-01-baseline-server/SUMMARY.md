# Week 01 Summary — First Hugging Face Baseline

## Date and environment

- Model: `Qwen/Qwen2.5-0.5B-Instruct`
- Device: Apple MPS (`mps`)
- PyTorch: `2.13.0`
- Transformers: `5.16.1`
- Generation: greedy/deterministic (`do_sample=false`)
- Maximum new tokens: `64`
- Warm-up requests per prompt: `1`
- Measured requests per prompt: `5`

## What I completed

1. Loaded the Hugging Face tokenizer and model.
2. Applied the model chat template to user messages.
3. Converted the formatted conversation into `input_ids` and `attention_mask`.
4. Ran non-streaming generation with `model.generate(..., use_cache=True)`.
5. Sliced the generated token IDs away from the input prompt IDs.
6. Decoded generated token IDs back into readable text.
7. Repeated short, medium, and long prompt tests five times each.
8. Exported the measurements to `baseline.json`.

## Results

The reported output-token rate below is an effective end-to-end rate because the notebook divides output tokens by total request latency. It is not decode-only throughput.

| Prompt | Input tokens | Output tokens | Median total latency | Approx. p95 from 5 runs | Effective output rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Short | 36 | 33 | 0.549 s | 0.562 s | 60.09 tok/s |
| Medium | 45 | 64 | 1.066 s | 1.067 s | 60.03 tok/s |
| Long | 1,111 | 64 | 1.358 s | 1.501 s | 47.12 tok/s |

The short prompt stopped at 33 tokens. The medium and long prompts reached the 64-token limit, so those outputs were capped by the generation setting rather than naturally ending.

## Interpretation

### Model path worked

The model loaded and generated repeatable deterministic responses on MPS. The five repeated runs for each prompt are close together, which is a useful first sign that the warm path is stable.

### Longer input increased total latency

The 1,111-token prompt took about 1.36 seconds at the median, compared with about 0.55 seconds for the 36-token prompt. This is consistent with additional prefill work for a longer input.

### Output generation was capped

The medium and long prompts both generated 64 tokens. Their total latency therefore includes the same maximum number of decode steps, while the long prompt adds more prefill work.

### The long prompt had a lower effective rate

The long prompt produced about 47 effective output tokens per second compared with about 60 for the shorter prompts. This rate includes prefill, so it should not yet be interpreted as pure decode speed.

## What this result does not prove yet

This file does not yet contain:

- streaming TTFT;
- per-token inter-token latency;
- queue time;
- client/network overhead;
- concurrency behavior;
- GPU memory or utilization;
- a quality score;
- a Hugging Face server HTTP benchmark.

Therefore this is a valid first local generation baseline, but it is not yet the complete production-serving baseline required by the Week 01 acceptance criteria.

## Next tests

1. Run the streaming cell and record TTFT, total streaming latency, and emitted chunks.
2. Run `streaming-and-missing-metrics.ipynb` to record per-token timing and save `streaming-metrics.json`.
3. Add explicit process/model-load cold-start measurements.
4. Run the same request through the Week 01 HTTP server.
5. Save the exact environment output with `python --version`, `uv pip list`, device, and model revision.
6. Build the Week 02 gateway and repeat one streaming and one non-streaming request through port `8000`.

## Evidence

- Raw result: `baseline.json`
- Notebook: `practical-baseline.ipynb`
- Streaming metrics notebook: `streaming-and-missing-metrics.ipynb`
- Practical plan: `PRACTICAL-TESTING-TODAY.md`
