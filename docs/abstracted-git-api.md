# Abstracted Git API

The repository intentionally hides the Git command model behind a higher-level AI-VCS abstraction. The goal is to let the user reason in terms of intent, sessions, and validation instead of raw Git operations.

## Design principle

Git remains the storage and transport substrate. The AI-VCS layer defines the user-facing model.

## Abstracted commands

### 1. `repo health`

Replaces: `git status`

Meaning: summarize whether the repo is in a valid state for a new session or release.

Returns:
- current session readiness
- untracked files
- drift warnings
- spec mismatch warnings
- validation status

### 2. `session start`

Replaces: `git init` and new working state setup

Meaning: begin a new session with explicit intent and scope.

Inputs:
- session id
- intent
- domain
- spec reference
- parent session

### 3. `session stage`

Replaces: `git add`

Meaning: mark the working state as part of a session’s outcome.

This is not just file staging; it is recording the state as a meaningful artifact of the current session.

### 4. `session finalize`

Replaces: `git commit`

Meaning: complete the session and store the snapshot as a validated unit of history.

Required metadata:
- intent
- spec version
- agent role
- validation result
- domain/contract boundary
- changed paths

### 5. `history view`

Replaces: `git log`

Meaning: inspect session lineage rather than raw commit chronology.

Shows:
- session ids
- parent session
- touched domain
- spec version
- validation status
- summary of intent

### 6. `history diff`

Replaces: `git diff`

Meaning: summarize differences in terms of session delta and intent, not raw patch lines.

This should explain:
- what behavior changed
- what spec or contract it is tied to
- which validation passed or failed

### 7. `debug trace`

Replaces: `git blame` and raw patch archaeology

Meaning: explain regression causes in session terms.

This should answer:
- which session introduced the change
- what its intent was
- which spec or contract it affected
- whether it was validated or drifted

### 8. `publish`

Replaces: `git push`

Meaning: transport the validated session state to the remote only after intent and validation checks pass.

Publish requires:
- session finalized
- spec aligned
- tests passing
- review artifact generated or ready

### 9. `release`

Replaces: tag/release semantics layered on Git

Meaning: create a versioned release from a validated session lineage.

This should map to semantic versioning rules and must be tied to a recorded validated session state.

## Core model

The system should present these concepts instead of Git jargon:

- session
- intent
- spec version
- contract boundary
- validation result
- release evidence
- historical lineage

## Why this matters

This abstraction prevents the repo from being a thin wrapper around Git commands. It turns the project into a system that reasons about developer intent, session state, and evidence, while Git remains the low-level durability and transport mechanism.
