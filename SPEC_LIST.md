# Global specification list

This document tracks the design and implementation status for the AI-native VCS prototype. It must remain in the repository and be tied to the issue backlog so that architecture drift is visible and reviewable.

## Implemented / satisfied

- [x] Git-backed snapshot storage for session artifacts.
- [x] Append-only per-path session history stored in an index instead of raw git log.
- [x] Session records that capture domain, agent, prompt, spec, commit, and changed paths.
- [x] Review-artifact scaffolding for spec deltas and ambiguity tracking.
- [x] Regression bisecting over session history using the test suite as oracle.
- [x] CLI scaffolding for init, specs, agents, sessions, logs, reviews, and bisecting.
- [x] Agentic workflow conventions documented in `AGENTS.md`.
- [x] CI and spec-progress automation added under `.github/workflows`.
- [x] Specialized agent roles and session metadata model documented in `docs/agent-roles.md`.

## Planned / future work

- [ ] Contract-level conflict prevention across active domains.
- [ ] Drift detection between spec, implementation, and generated outputs.
- [ ] Merge and concurrency semantics for simultaneous agent sessions.
- [ ] Better UX for human-facing history inspection without exposing git internals.
- [ ] Scalability of session metadata and snapshot storage at project size.
- [ ] Decide whether Python is the long-term core language or just the agent/orchestration layer.
- [ ] Evaluate Go as the long-term core VCS runtime while preserving the Python prototype for agent orchestration and experimentation.
- [ ] Define a robust, open-standard agent workflow spanning issue tracking, specs, and automation.

## Related future issues

- Parent: #1 — AI-native VCS design tradeoff — wrapping Git instead of replacing it.
- Future: #2 — Why wrap Git instead of implementing a separate VCS.
- Future: #3 — Why per-session history instead of git diff/blame.
- Future: #4 — Why deterministic tests are the review authority.

## Drift / defect policy

Any drift, bug, bad design, or architectural concern discovered during implementation must be captured as a future issue or spec-drift issue and reflected in this file as soon as the project direction is confirmed.
