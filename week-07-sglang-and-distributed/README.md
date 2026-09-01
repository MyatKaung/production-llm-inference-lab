# Week 07 - SGLang and Distributed Strategies

## Mini-project: compare inference engines

Add SGLang and speculative decoding, then decide from measurements when vLLM or SGLang is the better backend for this workload.

## Read

- HLSO: Chapter 7, `Speculative Decoding`, `Hands-on Speculative Decoding`, `Multi-GPU and Multi-Node Inferencing`, `Tensor Parallelism and Pipeline Parallelism`, `Prefill-Decode Disaggregation`, and `Advanced KV Caching`.
- DAS: Chapter 7, `SGLang core theory`, `RadixAttention`, `Router-based distributed architecture`, `Session affinity and cache locality`, `Fault tolerance`, `Speculative Decoding`, and `Production deployment patterns`.
- AISPE PDF: Chapter 15, pages 663-699; focus on disaggregated prefill/decode, TP/PP/EP/DP, speculative decoding, dynamic routing, and load balancing.

## Do

Add SGLang as a second backend. Compare prefix-heavy multi-turn traffic against vLLM. Run one speculative-decoding before/after test using the Week 3 quality gate. Test one parallelism strategy if two GPUs are available.

## Test today

Run the same prefix-heavy conversation trace through vLLM and SGLang. Keep model revision, tokenizer, sampling, prompts, concurrency, warm-up, and measurement window fixed. Compare TTFT, ITL, throughput, cache behavior, memory, and quality.

For speculative decoding, use a fixed draft model and target model. Measure acceptance rate, latency, throughput, memory, and quality. Test both short and long outputs; speculative decoding may help decode-heavy traffic but lose on short or poorly matching generations. If only one GPU is available, validate backend routing and replica failure behavior instead of pretending to have a distributed result.

## Output

Speculative-decoding raw results, vLLM-versus-SGLang comparison, and framework-selection ADR.

## Done when

- [ ] The comparison uses the same quality gate as earlier weeks.
- [ ] The ADR states which workload favors each framework and why.
- [ ] Speculative decoding has a before/after result and acceptance rate.
- [ ] Unsupported multi-GPU claims are clearly labeled as design-only.

## Course alignment

Course Weeks 7-8: inference optimization and distributed serving.
