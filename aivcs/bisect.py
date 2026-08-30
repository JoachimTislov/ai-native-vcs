"""Bisection.

"Bug attribution = bisection over the session array using the deterministic
test suite, replaying prior sessions' file states to find the first
session that flips a test from pass to fail."

This is `git bisect`'s binary-search idea, but: the "commits" being searched
are the session IDs recorded in a path's index history (index.py), not raw
git history, and the oracle is always the automated test command — never a
human "good"/"bad" judgment.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .index import SessionIndex
from .session import SessionRunner
from .store import Store


@dataclass
class BisectResult:
    first_bad_session: Optional[str]
    checked: list[str]


def _test_passes(root: Path, test_cmd: str) -> bool:
    result = subprocess.run(test_cmd, shell=True, cwd=root, capture_output=True)
    return result.returncode == 0


def bisect_path(root: Path, path: str, test_cmd: str) -> BisectResult:
    """Binary-search a path's session history for the first session after
    which `test_cmd` starts failing. Assumes monotonicity (once broken,
    stays broken) within the searched range, same as git bisect.
    """
    runner = SessionRunner(root)
    store = Store(root)
    history = SessionIndex(root / ".aivcs" / "index.json").history(path)
    checked: list[str] = []

    if not history:
        return BisectResult(first_bad_session=None, checked=checked)

    original_ref = store.head()
    try:
        lo, hi = 0, len(history) - 1
        # Sanity: if even the last session passes, nothing to find.
        commit = runner.load_record(history[hi]).commit_sha
        store.checkout(commit)
        checked.append(history[hi])
        if _test_passes(root, test_cmd):
            return BisectResult(first_bad_session=None, checked=checked)

        result_idx = hi
        while lo <= hi:
            mid = (lo + hi) // 2
            sid = history[mid]
            commit = runner.load_record(sid).commit_sha
            store.checkout(commit)
            checked.append(sid)
            if _test_passes(root, test_cmd):
                lo = mid + 1
            else:
                result_idx = mid
                hi = mid - 1

        return BisectResult(first_bad_session=history[result_idx], checked=checked)
    finally:
        if original_ref:
            store.checkout_ref(original_ref)
