# aivcs — Phase 1 scaffold

An AI-native version control system, built from `Core_Specifications`:
specs are the source of truth, sessions (not commits) are the atomic unit
of history, conflicts are checked at the contract level, and a deterministic
test suite — not human review — is the arbiter of correctness.

This is the **Phase 1** bootstrap: enough working plumbing to run real
sessions, track their history per file, generate review artifacts, and
bisect regressions. It was built with ordinary development because the
system can't build itself before it exists. From here on, further work on
this tool should be routed *through* `aivcs session run` itself.

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

This repository follows an agentic workflow aligned with the repo's
`AGENTS.md` conventions:

- `SPEC_LIST.md` remains the canonical project-tracker for satisfied vs.
  planned work.
- architecture questions are meant to become future issues, not hidden local
  decisions.
- bugs, drift, and bad design decisions must flow back into the spec and the
  issue tracker so the system can self-correct.
- GitHub Actions enforces the minimal automation required to keep the repo
  coherent: tests and spec-progress validation run on push/PR.

## Specialized agent roles

The project is designed to evolve around a small mesh of specialized agents,
with each one responsible for a distinct part of the workflow.

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

The `Abstraction Evaluator` is the design-focused specialist that checks the
boundary between Git as substrate and the AI-native session/spec model as the
user-facing system. The role is defined in `manifests/agent-manifest.yaml`.

## Provider-agnostic execution model

The runtime should be provider-neutral. The repo abstracts the AI backend so
that the same session flow can work with Claude, Copilot, OpenAI, or future
providers.

A concrete provider may support resume semantics such as `--resume`, but the
core system treats resume as an optimization rather than a source of truth.
The session remains the canonical object regardless of which provider produced
it.

The provider-neutral execution model is captured in `manifests/provider-agnostic-flow.yaml`.

## Python suitability at scale

Python is a good fit for the current phase because this project is about
prototyping AI orchestration, spec-driven development, and review automation.
It is not the strongest long-term core language for a high-scale VCS engine,
where Rust, Go, or JVM-native code may offer better concurrency, memory
safety, and throughput. The recommendation is to keep Python at the AI and
workflow layer while moving the hot-path storage/indexing engine to a lower-
level runtime when scale demands it.

The language tradeoff is captured in `manifests/python-at-scale.yaml`.

## Release flow and semantic versioning

This repository follows semantic versioning for releases: `MAJOR.MINOR.PATCH`.
The release workflow is intentionally conservative:

- only a validated, tested branch can be released
- the project version is incremented in `pyproject.toml`
- a release tag is created in the repo
- the tag is pushed together with the release commit

The release automation is in `.github/workflows/release.yml` and
`scripts/release.sh`.

## Quickstart

```bash
pip install -e .              # needs claude-agent-sdk + an ANTHROPIC_API_KEY to run live sessions

aivcs init                    # in an empty/existing project directory

# 1. Write a spec
aivcs spec new checkout ./checkout-spec.md
aivcs spec show checkout

# 2. Define a primitive agent (base instructions + default toolset)
cat > prompt.txt <<'EOF'
You are a careful backend engineer. Make the minimal change that satisfies
the spec. Never touch files outside your assigned domain.
EOF
aivcs agent add-primitive backend-engineer --system-prompt-file prompt.txt

# 3. Compound it to a domain + contract
aivcs agent add-compounded checkout-impl \
    --primitive backend-engineer \
    --domain src/checkout \
    --surface "POST /checkout,CheckoutService.charge"

# 4. Run a session
# Either pass a prompt directly or pipe it in via stdin / interactive input
# Example:
aivcs session run --agent checkout-impl --spec checkout \
    --prompt "Implement the charge endpoint per the spec."
# or:
printf '%s\n' "Implement the charge endpoint per the spec." | aivcs session run --agent checkout-impl --spec checkout

# 5. Inspect history, not diffs
aivcs log src/checkout/charge.py

# 6. Generate the review artifact for a session
aivcs review <session_id>

# 7. When something breaks, bisect instead of git blame
aivcs bisect src/checkout/charge.py --test "pytest tests/test_checkout.py -q"
```

## Tests

```bash
pytest tests/ -q
```

The test suite covers store/index/spec plumbing and, most importantly,
end-to-end bisection: three simulated sessions (two good, one regressing)
and a check that `bisect_path` finds the exact regressing session ID via
binary search — without ever consulting `git diff` or a human.
