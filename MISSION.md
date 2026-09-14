# Mission: Production LLM Inference Lab

## Why

Build and explain a defensible LLM-serving system, starting with a single local model and progressing only when each serving layer is measured and tested.

## Success looks like

- I can trace one chat request from HTTP JSON through tokens to generated output.
- I can build and verify a gateway, then justify later performance and deployment choices with measurements.

## Constraints

- Learn by working from the actual repository and measured local runs.
- Keep the first baseline on a small model and avoid adding distributed complexity before the single-server path is proven.

## Out of scope

- Premature batching, quantization, vLLM, SGLang, or Kubernetes work before the gateway milestone.
