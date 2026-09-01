# Practical Testing Today — Week 01 and Week 02

This is the notebook-first version of today's work. Start with the Week 01 notebook, then use the results to build and test the Week 02 gateway.

## Today's outcome

```text
Jupyter notebook -> Hugging Face model
client           -> gateway :8000 -> model server :8001 -> model
```

You are done when the model generates text, streaming and non-streaming behavior are tested, baseline timings are recorded, and the gateway contract tests pass.

## Model

Use:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

It is intentionally small for a first local test. Record the model ID and revision in the notebook output. Do not change model, device, sampling settings, or token limits during the baseline run.

## Apple device choice: MPS versus MLX versus CUDA

For today's notebook, use **Transformers on MPS**:

```text
Hugging Face Transformers -> PyTorch -> MPS/Metal -> Apple GPU
```

MPS is PyTorch's Apple GPU backend. It keeps today's experiment inside the Hugging Face/Transformers stack. The notebook automatically selects `mps` when available and falls back to CPU otherwise.

Do not use CUDA on this Mac; CUDA is for NVIDIA GPUs. Do not switch to MLX for the baseline: MLX is a separate Apple-native framework and would make the first result a different implementation. MLX is a good optional follow-up comparison after Weeks 01–02, but it is not today's baseline.

If an MPS operation is unsupported, record it and use `PYTORCH_ENABLE_MPS_FALLBACK=1` rather than silently changing the experiment.

## NVIDIA remote option

Yes, you can use the NVIDIA machine from this Mac. In that setup, the notebook and model run on the remote Linux machine; the Mac is only the client/editor. Use the remote GPU for the real Week 01 baseline and later CUDA-specific vLLM work.

From the Mac, connect without putting the password in a shell command:

```bash
ssh apcs@100.119.71.125
```

On the remote machine, verify the GPU and create the environment there:

```bash
nvidia-smi
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install torch transformers accelerate jupyter ipykernel fastapi uvicorn sse-starlette httpx pytest
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Copy or clone this repository on the remote machine, then run the notebook there:

```bash
uv run --python .venv/bin/python jupyter lab --no-browser --ip=127.0.0.1 --port=8888
```

In a second Mac terminal, create a private SSH tunnel:

```bash
ssh -N -L 8888:127.0.0.1:8888 apcs@100.119.71.125
```

Open `http://127.0.0.1:8888` on the Mac and select the remote environment. The notebook will choose `cuda` automatically because its device selection checks MPS first and CUDA second; on the remote NVIDIA machine MPS will be unavailable and CUDA will be selected.

For the gateway later, run the model server remotely on `127.0.0.1:8001`, then tunnel it to the Mac:

```bash
ssh -N -L 8001:127.0.0.1:8001 apcs@100.119.71.125
```

The Mac gateway can then call `http://127.0.0.1:8001`, while the model process remains on the NVIDIA machine. Keep the remote service bound to localhost unless you intentionally configure authentication and firewall rules.

Do not store the supplied SSH password in this repository, notebook output, shell history, or launch scripts. Prefer an SSH key and rotate the password after this setup if it is a shared or temporary credential.

## 1. Create the environment with uv

Run these commands from the repository root. Python 3.12 is chosen for a predictable PyTorch/Transformers environment; do not use the system Python 3.14 for this first setup.

```bash
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install torch transformers accelerate jupyter ipykernel fastapi uvicorn sse-starlette httpx pytest
python -m ipykernel install --user --name production-llm-inference-lab --display-name "Python (LLM Inference Lab)"
```

Verify the environment:

```bash
which python
python --version
uv pip list
python -c "import torch, transformers; print('torch', torch.__version__); print('transformers', transformers.__version__); print('MPS built:', torch.backends.mps.is_built()); print('MPS available:', torch.backends.mps.is_available())"
```

If `uv python install 3.12` says Python 3.12 is already installed, continue. If MPS is unavailable, use CPU and record that fact; the test is still valid.

## 2. Run the Week 01 notebook

Open:

```bash
uv run --python .venv/bin/python jupyter notebook week-01-baseline-server/practical-baseline.ipynb
```

Select the `Python (LLM Inference Lab)` kernel and run cells from top to bottom.

The notebook performs these tests:

1. Environment and device check.
2. Tokenizer/model load using the chat template.
3. One non-streaming generation smoke test.
4. One token-streaming smoke test.
5. Cold-start timing.
6. Warm timing for short, medium, and approximately 1K-token prompts.
7. JSON export to `baseline.json`.

The notebook detects whether Jupyter was launched from the repository root or from inside `week-01-baseline-server`, so the result is written to the correct Week 01 directory in either case.

Use these fixed generation settings for the baseline:

```text
temperature = 0.0, where supported
max_new_tokens = 64
do_sample = false
warm-up requests = 1
measured requests per prompt = 5
```

Record at least:

```text
prompt_tokens, output_tokens, TTFT, total_latency,
inter-token latency, output tokens/second, device, model revision
```

Report median and p95. Keep cold-start time separate from warm-request time.

## 3. Week 01 pass/fail tests

| Test | Pass condition |
| --- | --- |
| Model load | Loads once without out-of-memory error |
| Chat formatting | Uses `tokenizer.apply_chat_template` |
| Non-streaming generation | Non-empty text and token counts |
| Streaming generation | Ordered chunks and a final completion event |
| Warm request | Does not reload the model |
| Token limit | Output never exceeds `max_new_tokens` materially |
| Repeatability | Five runs produce comparable timing data |

## 4. Build the Week 02 gateway after the notebook

Use two processes:

```text
gateway:     http://127.0.0.1:8000/v1/chat/completions
model server:http://127.0.0.1:8001/generate
```

The client calls only port `8000`. The gateway owns request IDs, validation, timeout, cancellation, backend selection, and the OpenAI-compatible response shape. The model server stays an internal implementation detail.

### Gateway contract tests

Start with a fake backend and test:

| Test | Pass condition |
| --- | --- |
| Valid JSON request | OpenAI-shaped 200 response |
| Valid streaming request | Ordered SSE chunks and `[DONE]` |
| Missing/invalid messages | Structured 4xx response |
| Input/output token limit | Rejected before backend call |
| Backend timeout | Bounded timeout error |
| Backend 5xx | Mapped error includes request ID |
| Unknown backend | Clear validation/configuration error |
| Client disconnect | Cancellation is attempted |

Then run one non-streaming and one streaming request through the real Week 01 model server. Confirm that output, token counts, request ID, timeout behavior, and errors survive the gateway translation.

## 5. Evidence to save

```text
week-01-baseline-server/practical-baseline.ipynb
week-01-baseline-server/baseline.json
week-01-baseline-server/sequence-diagram.md
week-02-inference-gateway/tests/
today-environment.txt
```

Do not add batching, quantization, vLLM, SGLang, or Kubernetes today. First make this single-model path correct and measurable.
