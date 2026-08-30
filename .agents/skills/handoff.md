# Handoff skill

Use this only when a session must continue outside the ai-vcs interface. The goal is to capture the minimal, non-secret state needed for another agent or human to resume without guessing.

## Rule

- Store only repo-local, non-secret context.
- Never write tokens, API keys, passwords, or raw credentials.
- Prefer canonical repo paths and references over local environment details.
- If ai-vcs session metadata exists, prefer that source of truth; this is the fallback.

## Write path

Create a handoff note in the repo under:

- `.agents/handoffs/SESSION_ID.md`

If the repo does not yet have `.agents/handoffs/`, create it.

## Required content

```md
# Session handoff

- session_id: <uuid or stable identifier>
- timestamp_utc: <ISO-8601>
- repo_root: <repo-relative or absolute path>
- branch: <branch name>
- parent_session: <id if applicable>
- issue_or_spec: <issue # or spec name>
- objective: <one sentence>
- current_state: <what is already done>
- next_action: <what must happen next>
- validation: <last command run and result>
- blockers: <none or list>
- follow_up: <short list>
- model_provider: <provider/model if relevant>
- tool_summary: <notable tools / changes>
```

## Output sequence

1. Confirm the repo root and branch.
2. Record the session objective and latest validated state.
3. Record only the next requested action and any blockers.
4. Exclude secrets and tokens; replace them with placeholders.
5. Save the note in `.agents/handoffs/` and keep it concise.

This should not be necessary when using the ai-vcs interface, because the session metadata layer is the canonical handoff record.
