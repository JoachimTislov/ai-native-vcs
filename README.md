# aivcs — AI-native version control prototype

An AI-native version control system built around a simple principle:
intent, session history, and tests drive the workflow; Git remains the
storage and transport substrate.

The project treats specs as the source of truth, sessions as the atomic unit
of history, contracts as the domain boundary, and deterministic tests as the
review authority. It is designed to be provider-neutral at the workflow level,
so the same logic can adapt to Claude, Copilot, OpenAI, or future providers
without changing the underlying session model.

This repository now includes the agent framework, issue templates, release
workflow, and open-source repo standards that make the project usable as a
real engineering project rather than a one-off prototype.

## Current status

- Version: 0.0.1
- Session-first workflow: implemented
- Provider-agnostic agent flow: implemented via manifests
- GitHub issue and spec policy: implemented
- CI and release automation: implemented
- Python prototype retained for orchestration and experimentation
- Repository metadata and agent assets live under `.agents/`
- Canonical repo instructions are defined in `AGENTS.md` and surfaced via `.github/copilot-instructions.md`

## What's implemented

- `aivcs/store.py` — content-addressable storage on top of `git` (full
  snapshots per session, `git diff`/`blame` never exposed to the user).
- `aivcs/index.py` — the actual history model: an append-only array of
  session IDs per file/folder path.
- `aivcs/spec.py` — Specification store, versioned independently of
  sessions (`spec/<name>/v<N>.md`, never overwritten).
- `aivcs/agents.py` — Primitive agent specs and Compounded agents (a
  compounded agent = a primitive scoped to one domain + one contract).
- `aivcs/session.py` — the session runner: drives a Claude Agent SDK
  `query()` scoped to a compounded agent, commits the result as one
  snapshot, updates the index, records ambiguities the agent flagged.
- `aivcs/review.py` — renders the three-part review artifact (spec Δ,
  ambiguities resolved, tests newly passing).
- `aivcs/bisect.py` — binary search over a path's session-ID array using a
  test command as the oracle, to find the first regressing session.
- `aivcs/cli.py` — ties it together as `aivcs ...`.

## Not yet implemented (Phase 3+ per the research doc)

- Contract-level conflict prevention (blocking a session from starting if
  it would break a contract another active session's domain depends on).
  `models.Contract` exists as a data shape; nothing enforces it yet.
- Automated spec/primitive/session-fault classification after bisection.
- Drift detection (implementation vs. what regenerating from spec would
  produce).

## Agentic development model

This repository follows an agentic workflow aligned with `AGENTS.md` and the repo-local agent metadata under `.agents/`:

- `SPEC_LIST.md` remains the canonical tracker for satisfied vs. planned work.
- `AGENTS.md` is the single source of truth for repo policy and enforcement.
- `.agents/agents/*.yaml` stores the machine-readable role catalog and repo metadata.
- `.agents/skills/*.md` provides repo-local reusable skill handoff guidance.
- design questions are tracked through issues and labels, not as hidden local decisions.
- bugs, drift, and bad design decisions flow back into the spec and issue tracker so the system can self-correct.
- GitHub Actions enforces the minimal automation required to keep the repo coherent: tests and spec-progress validation run on push/PR.

## Specialized agent roles

The project is designed to evolve around a small mesh of specialized agents,
with each one responsible for a distinct part of the workflow.

- `Spec Steward` — owns spec and issue traceability.
- `Session Historian` — tracks session lineage and intent history.
- `Intent Diagnostician` — reconstructs what a session was trying to achieve.
- `Contract Guardian` — enforces domain and contract boundaries.
- `Test Oracle` — runs deterministic validation and bisects regressions.
- `Drift Auditor` — compares implementation to spec and detects drift.
- `Review Synthesizer` — turns session history into a review artifact.
- `Git Backend Steward` — owns Git snapshot semantics and replay.
- `Workflow Automation Agent` — maintains CI and issue/spec hygiene.
- `Abstraction Evaluator` — reviews whether the architecture still matches the
  project's goals and design principles.

The role definitions are stored in `.agents/agents/agent-manifest.yaml`, and the repo-local skill deck lives under `.agents/skills/`.

## Abstracted Git API

The repo deliberately hides the raw Git command model behind an intent-first,
session-first interface. The conceptual mapping is captured in the repository
manifests and automation scripts rather than in a dedicated docs directory.

In effect:

- `repo health` replaces `git status`
- `session start` replaces repo/bootstrap concerns
- `session stage` replaces `git add`
- `session finalize` replaces `git commit`
- `history view` replaces `git log`
- `history diff` replaces `git diff`
- `debug trace` replaces `git blame`
- `publish` replaces `git push`
- `release` replaces Git tagging/release semantics

This keeps Git as the durable engine while making the user-facing model a
session/spec workflow instead of raw version control commands.

The `Abstraction Evaluator` is the design-focused specialist that checks the
boundary between Git as substrate and the AI-native session/spec model as the
user-facing system. The role is defined in `.agents/agents/agent-manifest.yaml`.

## Provider-agnostic execution model

The runtime should be provider-neutral. The repo abstracts the AI backend so
that the same session flow can work with Claude, Copilot, OpenAI, or future
providers.

A concrete provider may support resume semantics such as `--resume`, but the
core system treats resume as an optimization rather than a source of truth.
The session remains the canonical object regardless of which provider produced
it.

The provider-neutral execution model is captured in `.agents/agents/provider-agnostic-flow.yaml`.

## Python suitability at scale

Python is a good fit for the current phase because this project is about
prototyping AI orchestration, spec-driven development, and review automation.
It is not the strongest long-term core language for a high-scale VCS engine,
where Rust, Go, or JVM-native code may offer better concurrency, memory
safety, and throughput. The recommendation is to keep Python at the AI and
workflow layer while moving the hot-path storage/indexing engine to a lower-
level runtime when scale demands it.

The language tradeoff is captured in `.agents/agents/python-at-scale.yaml`.

## Release flow and semantic versioning

This repository follows semantic versioning for releases: `MAJOR.MINOR.PATCH`.
The release workflow is intentionally conservative:

- only a validated, tested branch can be released
- the project version is incremented in `pyproject.toml`
- a release tag is created in the repo
- the tag is pushed together with the release commit
- the GitHub release includes generated binaries for the supported platforms

The release automation is in `.github/workflows/release.yml` and
`scripts/release.sh`.

This repo is also distributed under the MIT License; see `LICENSE`.

## Quickstart

```bash
# Install the project and its CLI
pip install -e .

# Create a local aivcs repo
mkdir -p demo && cd demo
aivcs init

# 1) Write a simple spec
cat > feature-spec.md <<'EOF'
# Feature spec
Implement the requested change in the target domain with the smallest possible edit.
EOF
aivcs spec new feature ./feature-spec.md
aivcs spec show feature

# 2) Define a primitive agent
cat > agent-prompt.txt <<'EOF'
You are a careful engineer. Keep the change minimal, focused, and testable.
EOF
aivcs agent add-primitive engineer --system-prompt-file agent-prompt.txt

# 3) Bind the agent to a domain
# The repo uses aivcs as the user-facing workflow; Git remains the storage backend.
aivcs agent add-compounded feature-impl   --primitive engineer   --domain src/feature   --surface "feature API"

# 4) Run a session
# Pass the prompt directly or pipe it in via stdin.
aivcs session run --agent feature-impl --spec feature   --prompt "Implement the change described in the spec."

# 5) Inspect session history through aivcs
# (not raw git log or git diff)
aivcs log src/feature

# 6) Review the latest session
# Replace <session_id> with the ID printed by the previous command.
aivcs review <session_id>

# 7) If the test suite regresses, bisect by session history
aivcs bisect src/feature --test "pytest -q"
```

This project keeps Git under the hood, but the user-facing workflow is the `aivcs` CLI: initialize, define specs, run sessions, inspect history, review output, and bisect regressions without exposing raw Git commands.

## Tests

```bash
pytest tests/ -q
```

The test suite covers store/index/spec plumbing and, most importantly,
end-to-end bisection: three simulated sessions (two good, one regressing)
and a check that `bisect_path` finds the exact regressing session ID via
binary search — without ever consulting `git diff` or a human.
