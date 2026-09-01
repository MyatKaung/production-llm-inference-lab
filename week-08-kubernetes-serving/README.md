# Week 08 - Production-Like Kubernetes Stack

## Mini-project: operate one production-like service

Deploy the gateway and model server on a single-node Kubernetes environment with probes, limits, telemetry, graceful shutdown, and rollback.

## Read

- HLSO: Chapter 4, `LLM Serving in Enterprise Systems`, `Public API Layer`, `Resource Management Layer`, `Model Selection and Orchestration Layer`, `Distributed Serving Layer`, `Core Inference Layer`, `Model Optimization Layer`, `Building with an Open Source Stack`, and `Build or Buy? Understanding Strategies`.
- DAS: Chapter 9, `Load balancing`, `Canary deployments and A/B testing`, `Observability`, `Reliability and fault tolerance`, `Cost optimization`, `Deploying LLM serving on kubernetes`, and `Multi-Model and Multi-Engine serving`.
- AISPE PDF: Chapter 3, pages 55-101; focus on `Container Runtime Optimizations for GPUs`, topology-aware Kubernetes, scheduling jitter, resource guarantees, OOM, and I/O isolation.

## Do

Deploy gateway, model server, Prometheus, and OpenTelemetry to a single-node production-like Kubernetes environment. Add probes, graceful shutdown, rate limiting, resources, and canary rollback.

## Test today

Deploy the smallest working stack. Verify service discovery, readiness before traffic, liveness after a stalled process, metrics scraping, trace propagation, and graceful termination while a stream is active. Exercise rate limiting and confirm the client receives a bounded error instead of an unbounded queue.

Deploy a deliberately different canary configuration, send a small percentage of traffic to it, compare its metrics, then roll it back. Inject one backend failure or kill one pod and record detection time, user-visible errors, recovery behavior, and lost in-flight requests.

## Output

Manifests or Helm chart, dashboard, failure notes, and operator runbook. Document multi-node autoscaling unless Week 6 data justifies deploying it.

## Done when

- [ ] Probes, resource requests/limits, shutdown, and rate limits are tested.
- [ ] Metrics and traces identify a request end to end.
- [ ] Canary and rollback are demonstrated.
- [ ] The runbook has startup, incident, rollback, and shutdown procedures.

## Course alignment

Course Weeks 6-8: production platform, resource management, and scaling architecture.
