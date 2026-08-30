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
aivcs session run --agent checkout-impl --spec checkout \
    --prompt "Implement the charge endpoint per the spec."

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
