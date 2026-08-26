# Week 02 - Inference Gateway

## Read

- HLSO: Chapter 3, `Build an Online LLM Serving Service from Scratch`, `Service Architecture`, `Implement Single Generation Request Handling`, `Batching`, `Streaming with Batching`, and `A General Design for Single-Model LLM Serving`.
- DAS: Chapter 9, `Anatomy of a production LLM serving system`, `Request routing and traffic management`, and `Routing strategies`.
- AISPE PDF: Chapter 1, pages 1-21; revisit `Benchmarking and Profiling` and `Cross-Team Collaboration` to define the gateway boundary and metrics contract.

## Do

In `02-inference-gateway`, implement `/v1/chat/completions`. Add streaming SSE, request IDs, timeout, cancellation, input/output token limits, backend adapters, and basic Prometheus metrics.

## Output

API contract tests, gateway sequence diagram, backend interface, and a working client that does not call the model server directly.

## Course alignment

Course Week 2: inference gateway and inference system design.

