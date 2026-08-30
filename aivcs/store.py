"""Storage layer.

Git's object model (blobs/trees/commits, content-addressed by hash, with
automatic dedup of identical content) is the default substrate for this system,
but the storage abstraction is intentionally generic so the same session logic
can run over other deterministic VCS CLIs as well.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from .vcs import GitBackend, VCSBackend, VCSRuntimeError, create_vcs_backend


class GitError(RuntimeError):
    pass


class Store:
    def __init__(self, root: Path, vcs: Optional[str] = None):
        self.root = Path(root)
        self.backend = create_vcs_backend(self.root, vcs)

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        return self.backend._run(args, check=check)

    def init(self) -> None:
        self.backend.init()

    def head(self) -> Optional[str]:
        return self.backend.head()

    def commit_all(self, message: str) -> str:
        return self.backend.commit_all(message)

    def changed_paths(self, sha: str, parent: Optional[str] = None) -> list[str]:
        return self.backend.changed_paths(sha, parent=parent)

    def checkout(self, sha: str) -> None:
        self.backend.checkout(sha)

    def checkout_ref(self, ref: str = "HEAD") -> None:
        self.backend.checkout_ref(ref)

    @property
    def vcs(self) -> str:
        return self.backend.plan.name
