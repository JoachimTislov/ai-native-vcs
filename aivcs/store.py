"""Storage layer.

Git's object model (blobs/trees/commits, content-addressed by hash, with
automatic dedup of identical content) is the right substrate for this system
— we don't need to reinvent snapshotting. What we deliberately do NOT do is
expose git's native history model to the user: no `diff`, no `blame`, no
commit-as-unit-of-review. A git commit here is just "the full snapshot a
session produced." The session-ID history that actually matters lives in
index.py, not in `git log`.

Each session's file contribution is stored as a FULL SNAPSHOT (a normal git
commit), not a patch — see the design-questions section of the research doc.
That makes bisection trivial: replaying session N is just `git checkout` of
that session's commit.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


class GitError(RuntimeError):
    pass


class Store:
    def __init__(self, root: Path):
        self.root = Path(root)

    # -- setup -----------------------------------------------------------

    def init(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._run(["init", "-q"])
        # An empty initial commit gives every domain a real parent to diff
        # against, so the very first session has a well-defined "before".
        if self._run(["log", "-1"], check=False).returncode != 0:
            self._run(["commit", "--allow-empty", "-q", "-m", "aivcs: init"])

    # -- low level ---------------------------------------------------------

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            ["git", "-C", str(self.root)] + args,
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            raise GitError(f"git {args} failed: {result.stderr.strip()}")
        return result

    # -- snapshotting --------------------------------------------------------

    def head(self) -> Optional[str]:
        r = self._run(["rev-parse", "HEAD"], check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    def commit_all(self, message: str) -> str:
        """Snapshot the entire working tree as one commit. Returns the commit sha."""
        self._run(["add", "-A"])
        # Allow empty commits: a session that concludes "no change needed" is
        # still a real session and should still get a session id / record.
        self._run(["commit", "-q", "--allow-empty", "-m", message])
        return self.head()

    def changed_paths(self, sha: str, parent: Optional[str] = None) -> list[str]:
        """Paths touched by `sha` relative to its parent (or `parent` if given).
        Used only to update the session index — never surfaced as a "diff" to
        the user.
        """
        base = parent or f"{sha}^"
        r = self._run(["diff", "--name-only", base, sha], check=False)
        if r.returncode != 0:
            # sha^ doesn't exist (root commit) -> everything in the tree counts
            r = self._run(["ls-tree", "-r", "--name-only", sha])
        return [p for p in r.stdout.splitlines() if p]

    def checkout(self, sha: str) -> None:
        """Replay a session's snapshot into the working tree (used by bisect)."""
        self._run(["checkout", "-q", sha, "--", "."])

    def checkout_ref(self, ref: str = "HEAD") -> None:
        self._run(["checkout", "-q", ref])
