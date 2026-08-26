# Week 08 - Production-Like Kubernetes Stack

## Mini-project: operate one production-like service

Deploy the gateway and model server on a single-node Kubernetes environment with probes, limits, telemetry, graceful shutdown, and rollback.

## Read

- HLSO: Chapter 4, `LLM Serving in Enterprise Systems`, `Public API Layer`, `Resource Management Layer`, `Model Selection and Orchestration Layer`, `Distributed Serving Layer`, `Core Inference Layer`, `Model Optimization Layer`, `Building with an Open Source Stack`, and `Build or Buy? Understanding Strategies`.
- DAS: Chapter 9, `Load balancing`, `Canary deployments and A/B testing`, `Observability`, `Reliability and fault tolerance`, `Cost optimization`, `Deploying LLM serving on kubernetes`, and `Multi-Model and Multi-Engine serving`.
- AISPE PDF: Chapter 3, pages 55-101; focus on `Container Runtime Optimizations for GPUs`, topology-aware Kubernetes, scheduling jitter, resource guarantees, OOM, and I/O isolation.

## Do

Deploy gateway, model server, Prometheus, and OpenTelemetry to a single-node production-like Kubernetes environment. Add probes, graceful shutdown, rate limiting, resources, and canary rollback.

## Output

Manifests or Helm chart, dashboard, failure notes, and operator runbook. Document multi-node autoscaling unless Week 6 data justifies deploying it.

## Course alignment

Course Weeks 6-8: production platform, resource management, and scaling architecture.
