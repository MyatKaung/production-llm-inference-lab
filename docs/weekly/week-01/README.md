# Week 01 - Request-to-Token Baseline

## Read

- HLSO: Chapter 2, `Executing LLM Generation: A Step-by-Step Walkthrough`, `Enable the KV Cache to Boost Performance`, `The Prefill and Decode Phases`, `LLM Streaming Serving Basics`, and `LLM Batch Serving Basics`.
- DAS: Chapter 1, `The modern AI model lifecycle`, `Inference: the prediction/generation phase`, `Serving: the production system`, and `Distributed inference: throughput scaling`.
- AISPE PDF: Chapter 1, pages 1-21; specifically `Benchmarking and Profiling`, `Measuring Goodput`, and `Transparency and Reproducibility`.

## Do

In `01-baseline-serving`, serve one small instruct model with Hugging Face Transformers. Expose streaming and non-streaming endpoints. Measure prompt tokens, output tokens, TTFT, inter-token latency, total latency, and throughput.

## Output

`baseline.json`, model-memory notes, launch command, smoke test, and request-to-token sequence diagram.

## Course alignment

Course Week 2: what happens when an LLM call is made.

