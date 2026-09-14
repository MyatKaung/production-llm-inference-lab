# Notebook source map

The two notebooks authored in the main lab folders below are original, lab-specific teaching material. They use the repository's Qwen/MPS baseline and are not copied course notebooks.

## Week 1 deep dive

- `week-01-baseline-server/01-prefill-decode-deep-dive.ipynb`
  - Extends this repository's `practical-baseline.ipynb` and `streaming-and-missing-metrics.ipynb` with an explicit forward-pass prefill and iterative cached decode loop.
  - Learning pattern inspired by [Abi Aryan's Class 1 notebook](https://github.com/goabiaryan/class-code/blob/main/class1/class1.ipynb): separate timing, prompt-length comparison, and reflection. No source cells were copied.
  - Reading alignment: HLSO Chapter 2; AISPE Chapter 1, as listed in `ROADMAP.md`.

## Week 2 gateway lab

- `week-02-inference-gateway/01-gateway-contracts-and-fake-backend.ipynb`
  - Builds an in-memory gateway contract test before the real Week 1 HTTP integration.
  - Learning pattern inspired by [Abi Aryan's Class 2 notebook](https://github.com/goabiaryan/class-code/blob/main/class2/class2.ipynb): model/server/gateway separation, controlled failure, and observability. It intentionally does not adopt that notebook's Docker/Modal dependency because this lab begins on the local Qwen/MPS path.
- `week-02-inference-gateway/02-real-week1-http-backend.ipynb`
  - Exercises the same public gateway contract through a real HTTP adapter to the local Week 1 Qwen server, in both normal and SSE streaming modes.
  - It is original lab material; it applies the same separation pattern without copying upstream cells or deployment scripts.
  - Reading alignment: HLSO Chapter 3 and DAS Chapter 9, as listed in `ROADMAP.md`.

## Primary documentation

- [Hugging Face caching](https://huggingface.co/docs/transformers/v5.15.1/cache_explanation)
- [Hugging Face generation](https://huggingface.co/docs/transformers/main_classes/text_generation)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

## Upstream reference material

- `class-code/` is a separate, unmodified checkout of [goabiaryan/class-code](https://github.com/goabiaryan/class-code) at revision `af42a485fedec72087ed7f25942a6dcbe8a07c7e` (checked 2026-09-13). It is reference material, not a lab artifact and not part of this lab's authored notebook set.
- No license file was present in that checkout when inspected. The main-lab notebooks therefore cite its ideas and links but do not copy its notebook cells, assets, or deployment scripts.
