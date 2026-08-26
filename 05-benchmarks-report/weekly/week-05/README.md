# Week 05 - vLLM Internals and Serving

## Read

- HLSO: Chapter 8, `vLLM`, `vLLM's Architecture`, `LLMEngine and EngineCore`, `Scheduler`, `ModelExecutor, (GPU) Worker, and ModelRunner`, `Generation-Request Execution Workflow`, and `vLLM's Layered Optimization Strategy`.
- DAS: Chapter 6, `Introduction to vLLM`, `Online inference`, `KV cache`, `PagedAttention`, `Overview of the vLLM architecture`, `Tensor Parallelism`, and `Hands-On examples`.
- AISPE PDF: Chapter 13, pages 527-602; focus on `Profiling PyTorch`, `PyTorch Profiler`, `CUDA Graphs`, `Scaling with PyTorch Distributed`, and `Continuous Integration and Performance Benchmarking`.

## Do

Serve the selected model with vLLM. Route the gateway to it. Compare Hugging Face and vLLM with the exact same workload and record server flags, memory use, batching, and failure limits.

## Output

Version-pinned vLLM launch config, integration test, profiler note, and baseline-versus-vLLM report.

## Course alignment

Course Weeks 4-5: inference engine internals and serving.

