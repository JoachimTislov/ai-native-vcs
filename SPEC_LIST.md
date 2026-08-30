# Global specification list

This document tracks the design and implementation status for the AI-native VCS prototype.

## Implemented / satisfied

- [x] Git-backed snapshot storage for session artifacts.
- [x] Append-only per-path session history stored in an index instead of raw git log.
- [x] Session records that capture domain, agent, prompt, spec, commit, and changed paths.
- [x] Review-artifact scaffolding for spec deltas and ambiguity tracking.
- [x] Regression bisecting over session history using the test suite as oracle.
- [x] CLI scaffolding for init, specs, agents, sessions, logs, reviews, and bisecting.

## Planned / future work

- [ ] Contract-level conflict prevention across active domains.
- [ ] Drift detection between spec, implementation, and generated outputs.
- [ ] Merge and concurrency semantics for simultaneous agent sessions.
- [ ] Better UX for human-facing history inspection without exposing git internals.
- [ ] Scalability of session metadata and snapshot storage at project size.

## Related future issues

- Parent: AI-native VCS design tradeoff — wrapping Git instead of replacing it.
- Child: Decide whether Git internals are an implementation substrate or user-facing model.
- Child: Clarify why session history is the primary axis of truth instead of blame/diff lineage.
- Child: Define how deterministic test suites become the review authority.
