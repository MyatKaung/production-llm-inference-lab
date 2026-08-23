# Limited Outsource Specification

This is a learning project. The owner writes and debugs every component that creates a system behavior or a performance number. Outsourcing is limited to mechanical repository chores.

## Allowed work

- Dockerfile cleanup after the owner has a working manual launch command.
- CI workflow wiring for tests the owner already wrote.
- Formatting, linting, dependency-update automation, and documentation link checks.
- Plot rendering from an owner-defined schema and owner-produced raw result files.
- Converting owner-written Kubernetes YAML into a Helm chart without changing runtime behavior.
- Reproducing a benchmark exactly as documented and reporting reproduction failures without tuning the system.

## Forbidden work

- Implementing the inference gateway, backend adapters, streaming, cancellation, routing, or rate limiting.
- Designing or implementing the benchmark harness, evaluation set, scorer, workload, SLO, or quality gate.
- Selecting models, hardware, framework versions, optimization flags, or parallelism strategy.
- Tuning vLLM/SGLang schedulers, batching, KV cache, quantization, speculative decoding, or distributed serving.
- Interpreting results, choosing a winning configuration, writing architecture decisions, or authoring the final report.
- Making an undocumented code or configuration change that could alter a reported number.

## Handoff requirements

Every outsourced change must be one narrowly scoped pull request with:

- a statement of what behavior is intentionally unchanged;
- commands for the owner to verify it;
- no generated benchmark conclusions;
- no secrets, model weights, book files, or raw private prompts;
- a clear list of every modified file.

The owner merges only after reading the diff and rerunning the relevant test or benchmark. Contractor output is support work, not portfolio authorship.
