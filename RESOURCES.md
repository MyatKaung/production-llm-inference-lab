# Production LLM Inference Resources

## Knowledge

- [FastAPI: Stream data](https://fastapi.tiangolo.com/advanced/stream-data/)
  Use for how `StreamingResponse` passes yielded chunks through an HTTP response.
- [Hugging Face Transformers: Generation](https://huggingface.co/docs/transformers/main_classes/text_generation)
  Use for `generate()`, `max_new_tokens`, and the streamer interface.
- [Hugging Face Transformers: Generation features](https://huggingface.co/docs/transformers/main/en/generation_features)
  Use for the rationale and mechanics of returning generated output incrementally.
- [Hugging Face Transformers: Caching](https://huggingface.co/docs/transformers/v5.15.1/cache_explanation)
  Use for why autoregressive generation needs a KV cache and how cached keys and values avoid recomputing prior context.
- [OpenAI API: Streaming events](https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal?lang=python)
  Use for the general server-sent-event model: an API can emit ordered events while a response is generated.
- [FastAPI: Handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
  Use for returning explicit client and dependency failures with HTTP status codes and structured details.
- [FastAPI: Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
  Use for replacing a real dependency with a test-only implementation.
- [pytest: monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
  Use for safely replacing network-dependent behavior during a test, with automatic cleanup afterward.

## Gaps

- The three course books named in `ROADMAP.md` are the primary learning texts, but their local copies are not part of this repository.
