# AGENTS.md

This repository follows an agentic development model: AI systems are contributors, not just tooling. The repository is designed to keep human intent, implementation, and verification aligned via specs, issue tracking, and tests.

## Mission

- Keep the AI-native VCS prototype grounded in a documented specification model.
- Treat issues and specs as the main long-lived design record.
- Route drift, defects, and architectural disagreements through the session/spec review path instead of leaving them implicit.

## Required workflow

1. Check `SPEC_LIST.md` before starting work.
2. If a task changes scope, architecture, or risk, create or update the relevant issue before patching code.
3. Keep implementation in sync with the global spec list and issue references.
4. Prefer targeted changes over broad refactors.
5. Run the smallest relevant validation command before considering the task complete.
6. If a bug, design flaw, or drift is identified, capture it in the spec system and issue tracker, not just in a local note.
7. Every task must be session-scoped, history-aware, and intent-driven.
8. Diagnose from original intent and session lineage before proposing a fix.

## Session-first model

The repository follows a session-centric development model rather than a raw patch model.

- Each task is treated as a session with explicit intent and traceability.
- Each session records spec version, domain, parent session, validation target, and result.
- History is tracked through sessions, not only through Git diff or blame.
- Diagnosis begins with the original intent, then moves to the failing implementation.

See `manifests/agent-manifest.yaml` for the full role architecture and session metadata schema.

## Spec and issue policy

- `SPEC_LIST.md` is the repo's canonical tracker for satisfied vs planned work.
- Parent and future design questions are tracked as issues, not as current implementation instructions.
- GitHub issue titles should be written without `Future:` or `Parent:` prefixes; use labels instead.
- Standard GitHub issue forms are preferred over plain markdown issue bodies when structured reporting is useful.
- New drift or defects discovered during implementation must be reflected in `SPEC_LIST.md` and linked to an issue when appropriate.
- Issue labels should follow the project conventions: `architecture`, `design`, `ai-vcs`, `spec`, and `release` as needed.

## Validation standard

- Python source must be validated with the repo's existing tests.
- New automation should be compatible with GitHub Actions and the local environment.
- No undocumented shortcuts: if a workaround is required, it should be captured in the spec or issue backlog.
