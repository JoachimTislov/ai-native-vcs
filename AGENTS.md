# AGENTS.md

This repository is spec-first, session-aware, and issue-driven. Keep the implementation aligned with `SPEC_LIST.md`, the active issue tracker, and the repo-local skill definitions under `.agents/skills/`.

## Mission

- Keep the AI-native VCS prototype grounded in a documented specification model.
- Treat issues and specs as the main long-lived design record.
- Route drift, defects, and architectural disagreements through the session/spec review path instead of leaving them implicit.

## Required workflow

1. Check `SPEC_LIST.md` before starting work.
2. If a task changes scope, architecture, or risk, create or update the relevant issue before patching code.
3. Keep implementation in sync with the global spec list and issue references.
4. Use the repo-local skills in `.agents/skills/<skill>/SKILL.md` for reusable task guidance; the skill description is the active instruction for that workflow.
5. Prefer targeted changes over broad refactors.
6. Run the smallest relevant validation command before considering the task complete.
7. If a bug, design flaw, or drift is identified, capture it in the spec system and issue tracker, not just in a local note.
8. Every task must be session-scoped, history-aware, and intent-driven.

## Repo structure

- `SPEC_LIST.md` is the canonical tracker for satisfied vs. planned work.
- `AGENTS.md` is the short policy layer; the detailed task workflows live in `.agents/skills/*/SKILL.md`.
- GitHub Copilot discovers repo-scoped custom agents under `.github/agents/*.agent.md`; this repo keeps the source files under `.agents/agents/*.agent.md` and mirrors them via a symlink to the GitHub path.
- Workflow scripts live next to the workflow that invokes them under `.github/workflows/scripts/`.
- If a script is only relevant to one skill or one agent, keep it next to that `SKILL.md` or custom-agent profile instead of in the shared workflow script directory.
- `.agents/handoffs/` stores concise continuation notes when a session must resume outside the primary interface.

## Commit and validation standard

- Use `.agents/skills/commit/SKILL.md` as the canonical local template for commit composition.
- Always append the required trailer: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
- Validate with the smallest existing test command that covers the changed behavior.
- Prefer deterministic repo automation and issue/spec traceability over local ad hoc decisions.
