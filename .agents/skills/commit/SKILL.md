---
name: commit
description: Write repository commits that match this project's session-first, Linux-kernel-inspired standards. Use when creating a commit message that must be concise, concrete, and include the required Copilot trailer.
---

# Commit skill

Use this skill when writing a repository commit that should match the project’s session-first and Linux-kernel-inspired standards.

## Required format

```text
<type>: <short summary>

Problem:
The issue, bug, or design drift this change addresses.

Impact:
Who or what is affected and why the change matters.

Changes:
- what changed
- what was kept out of scope
- any deterministic validation or enforcement added

Validation:
- command(s) run
- result(s)

References:
- issue numbers
- spec references
- session metadata IDs if applicable

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Rules

- Keep the subject line to 74 characters or fewer.
- Use imperative mood (`fix`, `add`, `remove`, `refactor`, `docs`).
- Keep the summary about the code change itself; do not narrate the whole session.
- Store detailed provenance outside Git in session metadata.
- Use the trailer exactly as written; it must be the final line of the message.
- The normal commit subject should be the change, not the entire AI workflow or session history.

## Example

```text
fix: set repo-local git identity for CI

Problem:
GitHub Actions runs without a configured user.name/user.email, so repository initialization fails during tests.

Impact:
New repositories created in CI or temp directories cannot commit snapshots, which breaks session-based workflow validation.

Changes:
- configure repo-local git identity in Store.init()
- ensure commit_all() also sets the same fallback identity
- keep the implementation local to the repository instead of relying on global git config

Validation:
- python -m pytest tests/test_core.py -q

References:
- issue: #n
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

This repo intentionally uses session metadata outside Git for provenance, while keeping Git commits small, explicit, and independently reviewable.
