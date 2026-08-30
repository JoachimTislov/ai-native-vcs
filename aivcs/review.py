"""Review artifact generator.

"Review artifact = a three-part diff: (1) spec version A->B, (2)
ambiguities the session resolved and how, (3) which test-suite criteria
newly pass."

Human judgment is reserved for approving part (1)/(2) — interpretation —
never part (3), which the test suite already settled. This module renders
that three-part artifact from a SessionRecord; it does not itself run
tests (see bisect.py / the CLI's `check` command for that), it only
reports what a test run already told the session.
"""

from __future__ import annotations

from .models import SessionRecord


def render(record: SessionRecord, spec_before: str | None, spec_after: str | None) -> str:
    lines = [f"# Review artifact — session {record.session_id}", ""]

    lines.append("## 1. Specification version A -> B")
    if record.spec_name:
        prev = (record.spec_version or 1) - 1
        lines.append(f"- spec: `{record.spec_name}` v{prev or '(none)'} -> v{record.spec_version}")
    else:
        lines.append("- no named specification was bound to this session")
    if spec_before is not None and spec_after is not None and spec_before != spec_after:
        lines.append("- spec text changed as part of this session")
    lines.append("")

    lines.append("## 2. Ambiguities resolved")
    if record.ambiguities:
        for a in record.ambiguities:
            lines.append(f"- {a.description}")
    else:
        lines.append("- none reported")
    lines.append("")

    lines.append("## 3. Test-suite criteria newly passing")
    if record.tests_newly_passing:
        for t in record.tests_newly_passing:
            lines.append(f"- {t}")
    else:
        lines.append("- (not yet checked — run `aivcs check <session_id> --test '<cmd>'`)")
    lines.append("")

    lines.append("## Files touched")
    for p in record.changed_paths:
        lines.append(f"- {p}")

    return "\n".join(lines)
