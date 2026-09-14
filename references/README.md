# Reference material

## `class-code`

The [`class-code`](class-code/) repository is included as a Git submodule from:

```text
https://github.com/goabiaryan/class-code.git
```

It is reference material, not part of this lab's implementation. The submodule is pinned to a commit so the examples remain reproducible.

## What to study now

### Class 2 — inference servers

Read `class-code/class2/` for ideas about:

- health endpoints;
- OpenAI-compatible chat requests;
- streaming responses with `curl -sN`;
- server anatomy;
- metrics and failure exercises.

Compare those ideas with this project’s Week 01 server. Do not copy the model, cloud commands, or dependency setup blindly: this lab currently uses `Qwen/Qwen2.5-0.5B-Instruct` and runs locally on MPS or remotely on CUDA.

### Class 7 — gateway and replicas

Read `class-code/class7/` after the Week 02 gateway exists. It is useful for understanding:

- gateway boundaries;
- rate limiting;
- routing to multiple model replicas;
- smoke tests;
- failure testing.

Those are later extensions. First make the single-backend gateway in `week-02-inference-gateway/` correct and testable.

## How it relates to the notebooks

Use the reference repository to compare server structure and operational behavior. Use [prefill-and-decode.ipynb](../week-01-baseline-server/prefill-and-decode.ipynb) for the model-level explanation, and use `class2` only as a second implementation reference. The examples may use different models, APIs, cloud runtimes, and metrics.

## How to update the reference

From the repository root:

```bash
git submodule update --remote --merge references/class-code
```

If the submodule changes, commit the updated submodule pointer in the main repository.
