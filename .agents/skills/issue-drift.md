# Issue drift detection

Use this skill when issue metadata, repository status, or spec records are out of sync.

## Goal

Catch drift early without loading the entire repository history or reading every file in the repo.

## Method

1. Read only the canonical tracker: `SPEC_LIST.md`.
2. Read only the policy file: `AGENTS.md`.
3. Query GitHub issues using the minimal `gh issue list --state all --json ...` shape.
4. Compare issue labels to the required taxonomy:
   - `ai` | `human`
   - `status:planned` | `status:in-progress` | `status:done`
   - `area:core` | `area:spec` | `area:docs` | `area:workflow` | `area:release`
   - `priority:low` | `priority:medium` | `priority:high`
   - `type:feature` | `type:spec` | `type:research` | `type:task`
5. If `SPEC_LIST.md` says an issue is implemented, the issue should reflect that via `status:done`.
6. If the repo policy has changed, update the issue taxonomy before editing implementation.

## Expected output

- A short list of issue numbers missing required labels.
- A list of issue numbers whose label state does not match the repo status.
- A recommendation to update the issue labels or the spec tracker, not both blindly.

This skill is intentionally lightweight: it limits reads to policy files and the issue index, which keeps session context small and deterministic.
