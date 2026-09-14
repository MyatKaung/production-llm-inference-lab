# Week 02 - Inference Gateway

## Mini-project: build an OpenAI-compatible gateway

Build a gateway that accepts one stable client API and can forward the request to the Week 1 model server without exposing backend details to the client.

## Read

- HLSO: Chapter 3, `Build an Online LLM Serving Service from Scratch`, `Service Architecture`, `Implement Single Generation Request Handling`, `Batching`, `Streaming with Batching`, and `A General Design for Single-Model LLM Serving`.
- DAS: Chapter 9, `Anatomy of a production LLM serving system`, `Request routing and traffic management`, and `Routing strategies`.
- AISPE PDF: Chapter 1, pages 1-21; revisit `Benchmarking and Profiling` and `Cross-Team Collaboration` to define the gateway boundary and metrics contract.

## Do

In `02-inference-gateway`, implement `/v1/chat/completions`. Add streaming SSE, request IDs, timeout, cancellation, input/output token limits, backend adapters, and basic Prometheus metrics.

## Test today

Use a fake backend first, then the Week 1 server. Test one successful request in each mode and these failure paths: malformed JSON, missing messages, too many input tokens, too many output tokens, backend timeout, backend 5xx, client disconnect during streaming, and unknown backend name.

For every request verify a request ID, bounded duration, structured error shape, and a metric increment. For streaming, verify that cancellation reaches the backend and that no tokens are emitted after cancellation. The client must call only the gateway URL.

## Output

API contract tests, gateway sequence diagram, backend interface, and a working client that does not call the model server directly.

## Guided notebook

Start with `01-gateway-contracts-and-fake-backend.ipynb`. It is executable on the local project environment and proves four gateway behaviors before a real model-server integration:

1. mapping a fixed backend result to a public chat-completion response;
2. rejecting an over-limit request before it reaches the backend;
3. mapping a controlled backend timeout to a bounded gateway error; and
4. relaying ordered fake stream chunks followed by `[DONE]`.

It adapts the useful teaching sequence from Class 2 without requiring its Docker/Modal deployment path. Provenance and reading alignment are in [`../NOTEBOOK-SOURCES.md`](../NOTEBOOK-SOURCES.md).

Then run `02-real-week1-http-backend.ipynb`. Start the Week 1 server on port 8001 first; the notebook checks `/health`, constructs an `HttpWeek1Backend`, and proves that the same gateway route translates both a real `/generate` result and real `/generate/stream` SSE chunks. The client still calls only `/v1/chat/completions`.

## Done when

- [ ] Contract tests pass without a real model.
- [ ] Integration tests pass against the Week 1 server.
- [ ] Non-streaming and SSE responses are OpenAI-compatible enough for the chosen client.
- [ ] Timeout, cancellation, limits, IDs, and backend errors are observable.

## Course alignment

Course Week 2: inference gateway and inference system design.
