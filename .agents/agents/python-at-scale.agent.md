---
name: python-at-scale
description: Design note explaining why Python is used for the prototype and orchestration layer, and when a compiled runtime may be evaluated.
---

# Python suitability at scale

Python is a good fit for the current phase because this project is about prototyping AI orchestration, spec-driven development, and review automation. It is not the strongest long-term core language for a high-scale VCS engine, where Rust, Go, or JVM-native code may offer better concurrency, memory safety, and throughput.

Recommendation:
- keep Python for AI orchestration, spec and session workflows, and validation
- evaluate a compiled runtime for the storage engine, indexing, and concurrency-bound metadata services
