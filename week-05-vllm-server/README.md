# Week 05 - vLLM Internals and Serving

## Mini-project: replace the baseline with vLLM

Deploy vLLM behind the existing gateway and explain the performance difference using its scheduler and KV-cache behavior.

## Read

- HLSO: Chapter 8, `vLLM`, `vLLM's Architecture`, `LLMEngine and EngineCore`, `Scheduler`, `ModelExecutor, (GPU) Worker, and ModelRunner`, `Generation-Request Execution Workflow`, and `vLLM's Layered Optimization Strategy`.
- DAS: Chapter 6, `Introduction to vLLM`, `Online inference`, `KV cache`, `PagedAttention`, `Overview of the vLLM architecture`, `Tensor Parallelism`, and `Hands-On examples`.
- AISPE PDF: Chapter 13, pages 527-602; focus on `Profiling PyTorch`, `PyTorch Profiler`, `CUDA Graphs`, `Scaling with PyTorch Distributed`, and `Continuous Integration and Performance Benchmarking`.

## Do

Serve the selected model with vLLM. Route the gateway to it. Compare Hugging Face and vLLM with the exact same workload and record server flags, memory use, batching, and failure limits.

## Test today

Pin the vLLM version and model revision. Start vLLM with the smallest viable configuration, call it through the gateway, and run the Week 3 benchmark unchanged. Confirm that streaming, token limits, timeouts, and errors still behave at the gateway boundary.

Compare Hugging Face and vLLM on identical prompts, output limits, concurrency, warm-up, and sample count. Inspect vLLM metrics or logs for scheduler behavior, KV-cache usage, running/waiting requests, and rejected requests. Add one profiler trace or timeline and use it to explain one observed difference.

## Output

Version-pinned vLLM launch config, integration test, profiler note, and baseline-versus-vLLM report.

## Done when

- [ ] The gateway can switch between the two backends without client changes.
- [ ] The comparison is apples-to-apples and reproducible.
- [ ] Memory and failure limits are explicit.
- [ ] At least one scheduler/KV-cache observation explains the result.

## Course alignment

Course Weeks 4-5: inference engine internals and serving.
