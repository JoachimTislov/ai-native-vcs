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

See `.agents/agents/agent-manifest.yaml` for the full role architecture and session metadata schema.

## Spec and issue policy

- `SPEC_LIST.md` is the repo's canonical tracker for satisfied vs planned work.
- Parent and future design questions are tracked as issues, not as current implementation instructions.
- GitHub issue titles should be written without `Future:` or `Parent:` prefixes; use labels instead.
- Standard GitHub issue forms are preferred over plain markdown issue bodies when structured reporting is useful.
- All issues must be classified deterministically by automation: `ai` for AI-originated work and `human` for human-originated work.
- Every issue must also carry a status label from `status:planned`, `status:in-progress`, or `status:done`, plus an area label from `area:core`, `area:spec`, `area:docs`, `area:workflow`, or `area:release`.
- Priority labels (`priority:low`, `priority:medium`, `priority:high`) and type labels (`type:feature`, `type:spec`, `type:research`, `type:task`) are required for triage and sorting.
- New drift or defects discovered during implementation must be reflected in `SPEC_LIST.md` and linked to an issue when appropriate.
- Issue labels should use standard GitHub labels and the repository taxonomy as needed; avoid repo-specific labels that duplicate standard categories.
- Issue metadata must be updated by automation or scripts instead of ad hoc manual labeling so the repo remains easy to sort and review.

## Validation standard

- Python source must be validated with the repo's existing tests.
- New automation should be compatible with GitHub Actions and the local environment.
- No undocumented shortcuts: if a workaround is required, it should be captured in the spec or issue backlog.

## Deterministic enforcement policy

- All repo enforcement must be deterministic and explicit: code, scripts, and GitHub rules should be the source of truth, not aspirational text or soft guidance.
- Branch naming, commit-message rules, linear-history requirements, and merge policy must be encoded in automation or repository settings rather than left to convention alone.
- The project must prefer machine-enforced constraints over human memory or loosely phrased instructions.
- CI and repository settings must agree on the same policy so that enforcement is consistent and reviewable.

## Sync and session policy

- A session may produce one or more child commits, but the authoritative session metadata must live outside Git and reference those child commits.
- Git commits should stay concise and declarative; the session record stores provider, model, duration, tool usage, MCP metadata, validation results, and spec references.
- The session history is the source of truth for debugging and review, not the commit narrative alone.
- The repo must not require the reader to reconstruct implicit context from commit messages; the session metadata must make the relationship explicit.
- A session should be independently reviewable even when multiple child commits are associated with it.

## Commit message standard

- Use a short summary line, imperative mood, and a maximum of 74 characters.
- Follow a Linux-kernel style structure: summary, blank line, problem, impact, changes, validation, references.
- Keep the summary focused on the change itself; do not encode the session history or implicit past reasoning in the message.
- Store detailed provenance outside Git in the session metadata record.
- Use `.agents/skills/commit.md` as the canonical local template for commit composition.
- Always append the required trailer at the end of the commit message: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
