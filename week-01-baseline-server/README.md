# Week 01 - Request-to-Token Baseline

## Mini-project: build a tiny inference server

Build one working Hugging Face server and make the first defensible measurement of how a request becomes prefill, decode, and streamed tokens.

## Read

- HLSO: Chapter 2, `Executing LLM Generation: A Step-by-Step Walkthrough`, `Enable the KV Cache to Boost Performance`, `The Prefill and Decode Phases`, `LLM Streaming Serving Basics`, and `LLM Batch Serving Basics`.
- DAS: Chapter 1, `The modern AI model lifecycle`, `Inference: the prediction/generation phase`, `Serving: the production system`, and `Distributed inference: throughput scaling`.
- AISPE PDF: Chapter 1, pages 1-21; specifically `Benchmarking and Profiling`, `Measuring Goodput`, and `Transparency and Reproducibility`.

## Do

In `01-baseline-serving`, serve one small instruct model with Hugging Face Transformers. Expose streaming and non-streaming endpoints. Measure prompt tokens, output tokens, TTFT, inter-token latency, total latency, and throughput.

## Test today

Run the same prompt through both endpoints after one warm-up request. Use a short prompt and a longer prompt, then request a fixed output length. Repeat each case at least 5 times and report median plus p95.

Verify that:

- non-streaming returns valid JSON and the complete generated text;
- streaming emits ordered chunks and ends with a clear completion event;
- token counts are measured with the model tokenizer, not character length;
- TTFT starts at request acceptance and total latency ends at the final token;
- an invalid request returns a useful 4xx response.

First write a hypothesis such as: “decode time will grow with output tokens, while TTFT will grow with prompt length.” The result belongs in `baseline.json`.

## Output

`baseline.json`, model-memory notes, launch command, smoke test, and request-to-token sequence diagram.

## Done when

- [ ] One command starts the server.
- [ ] Streaming and non-streaming tests pass.
- [ ] Cold and warm behavior are separated.
- [ ] The report contains TTFT, TPOT/ITL, end-to-end latency, throughput, and token counts.

## Course alignment

Course Week 2: what happens when an LLM call is made.
