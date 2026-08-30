# Agent roles for session-scoped, intent-aware development

This repository adopts a session-first development model. The system is structured around a small set of specialized agents whose job is to reason over intent, spec, history, and validation, not just to emit patches.

## Design principle

Every task belongs to a session. A session is the atomic unit of work and carries intent, context, and evidence.

A session should answer the following questions:

- What was the intent?
- Which spec or issue was it built from?
- Which parent session or prior state did it inherit?
- Which domain or contract was in scope?
- What was validated and how?
- What was the final artifact or outcome?

This makes diagnosis and review history-aware instead of patch-centric.

## Agent roles

### 1. Spec Steward

Owns the canonical spec state and issue/spec linkage.

Responsibilities:
- maintain `SPEC_LIST.md` and issue references
- ensure tasks map to a spec or issue before execution
- version specs and track changes over time
- reject work that has no traceable intent

### 2. Session Historian

Owns session lineage and historical traceability.

Responsibilities:
- record session metadata for each task
- track parent session, domain, prompt, changed files, and outcome
- index session history by path and by domain
- expose causal relationships across sessions for debugging

### 3. Intent Diagnostician

Reconstructs the original intent behind a failing or regressing session.

Responsibilities:
- compare the current state against the parent session and the spec
- answer what the session was trying to achieve
- explain regressions in terms of intent drift, not just code churn
- produce an initial diagnosis before patching

### 4. Contract Guardian

Owns the domain boundaries and contract surface.

Responsibilities:
- verify the agent stays inside its assigned domain
- block work that crosses contracts or scope boundaries
- validate that a change matches the declared surface of the domain

### 5. Test Oracle

Owns verification and deterministic pass/fail signals.

Responsibilities:
- run the smallest relevant tests for the session
- track pass/fail evidence
- support bisect and regression analysis
- prevent subjective review from replacing evidence

### 6. Drift Auditor

Owns long-term consistency between design intent and implementation.

Responsibilities:
- compare code against specs and generated artifacts
- identify stale assumptions and outdated session histories
- record design drift as issues or spec updates

### 7. Review Synthesizer

Owns the human-readable session review output.

Responsibilities:
- summarize spec delta, ambiguities, and tests
- render the review artifact from session and spec history
- connect implementation changes back to intent and evidence

### 8. Git Backend Steward

Owns the underlying Git substrate and snapshot semantics.

Responsibilities:
- manage Git snapshots, checkout, and replay for bisecting
- keep Git as an implementation detail, not the user-facing truth
- ensure the session model remains the canonical history model

### 9. Workflow Automation Agent

Owns CI, issue lifecycle, and repo hygiene.

Responsibilities:
- maintain GitHub workflows and repo automation
- check spec-progress integrity
- surface drift and defects in issue trackers
- keep docs and agent conventions synchronized

## Required session metadata

Each session should record the following fields:

- session_id
- parent_session_id (optional)
- created_at
- agent_name
- agent_role
- prompt
- intent
- spec_name
- spec_version
- domain
- contract_surface
- changed_paths
- commit_sha
- parent_sha
- status (running, succeeded, failed, drifted)
- validation_command
- validation_result
- ambiguity_notes
- issue_refs
- notes

This metadata is the backbone of reasoned debugging and future work.

## Suggested session record schema

```json
{
  "session_id": "uuid",
  "parent_session_id": "uuid-or-null",
  "created_at": "2026-08-30T14:00:00Z",
  "agent_name": "intent-diagnostician",
  "agent_role": "Intent Diagnostician",
  "prompt": "Diagnose why charge endpoint regressed after the last session.",
  "intent": "Restore checkout charge semantics without widening scope.",
  "spec_name": "checkout",
  "spec_version": 3,
  "domain": "src/checkout",
  "contract_surface": ["POST /checkout", "CheckoutService.charge"],
  "changed_paths": ["src/checkout/charge.py", "tests/test_checkout.py"],
  "commit_sha": "abc123",
  "parent_sha": "def456",
  "status": "failed",
  "validation_command": "pytest tests/test_checkout.py -q",
  "validation_result": {
    "exit_code": 1,
    "summary": "payment assertion regression"
  },
  "ambiguity_notes": [
    "The previous session changed validation semantics without updating the contract."
  ],
  "issue_refs": ["#3", "#5"],
  "notes": "The issue was not a raw diff problem; it was an intent mismatch with the spec."
}
```

## Working rule

Every session should be understandable in terms of:

- intent
- spec
- lineage
- validation
- outcome

If a change cannot be explained this way, it is not yet a valid, traceable session.

## Future development direction

The repo should continue to evolve along these principles:

- sessions are the primary history unit
- agents are specialized by responsibility
- diagnosis begins with intent reconstruction
- drift and defects are piped back into the repo via issue/spec tracking
- Git remains a storage substrate, not the user-visible source of truth
