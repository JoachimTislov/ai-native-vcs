---
name: abstracted-git-api
description: Design note describing the abstraction between Git as a storage backend and the session-oriented user model.
---

# Abstracted Git API

The repository deliberately hides the raw Git command model behind an intent-first, session-first interface.

- `repo health` replaces `git status`
- `session start` replaces repo/bootstrap concerns
- `session stage` replaces `git add`
- `session finalize` replaces `git commit`
- `history view` replaces `git log`
- `history diff` replaces `git diff`
- `debug trace` replaces `git blame`
- `publish` replaces `git push`
- `release` replaces Git tagging and release semantics

Git remains the durable engine; the user-facing model is session and spec driven.
