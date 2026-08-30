# Python at scale for the AI-native VCS

## Short answer

Python is a strong choice for the prototype and for the AI orchestration layer, but it is not the strongest long-term default for the performance-critical core of a large-scale version control system.

## Why Python is suitable here

- Fast iteration for research and prototyping.
- Excellent ecosystem for CLI tooling, test automation, and AI integrations.
- Easy to express spec-driven workflows and session orchestration.
- Good fit for a system where correctness is driven by deterministic tests and AI-assisted review.

## Where Python becomes limiting

- CPU-intensive snapshot processing at large repository scale.
- Tight concurrency and memory-safety requirements in a core VCS engine.
- High-throughput indexing, file watching, and storage operations.
- Long-lived systems where latency and operational predictability matter more than prototyping speed.

## Recommendation

Use Python for:

- the AI workflow layer,
- scripts, automation, and orchestration,
- the session/spec review model,
- validation and experimentation.

Use a compiled language such as Rust, Go, or Java/Kotlin for:

- the performance-sensitive storage engine,
- high-scale indexing and diffing,
- concurrency-heavy metadata services,
- long-lived production-grade VCS internals.

## Final view

For this repository, Python is the right language for the current phase because the project is about designing a workflow and proving an architecture. At scale, the system should likely keep Python at the orchestration boundary while moving the hot path into a lower-level runtime.
