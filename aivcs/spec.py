"""Specification store.

"Version-controlled independently of sessions; not tied to any single
session so it can be referenced flexibly without going stale; changes
produce a new spec version, old sessions can still reference prior
versions."

Implementation: each named spec lives under `spec/<name>/v<N>.md`. Old
versions are never deleted or rewritten — a new version is always a new
file — so any SessionRecord's `spec_version` stays resolvable forever, even
after the spec has moved on.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


class SpecStore:
    def __init__(self, root: Path):
        self.root = Path(root) / "spec"

    def _dir(self, name: str) -> Path:
        return self.root / name

    def versions(self, name: str) -> list[int]:
        d = self._dir(name)
        if not d.exists():
            return []
        out = []
        for f in d.glob("v*.md"):
            m = re.match(r"v(\d+)\.md$", f.name)
            if m:
                out.append(int(m.group(1)))
        return sorted(out)

    def latest_version(self, name: str) -> Optional[int]:
        vs = self.versions(name)
        return vs[-1] if vs else None

    def new_version(self, name: str, content: str) -> int:
        d = self._dir(name)
        d.mkdir(parents=True, exist_ok=True)
        v = (self.latest_version(name) or 0) + 1
        (d / f"v{v}.md").write_text(content)
        return v

    def get(self, name: str, version: Optional[int] = None) -> str:
        v = version or self.latest_version(name)
        if v is None:
            raise FileNotFoundError(f"no spec named {name!r}")
        return (self._dir(name) / f"v{v}.md").read_text()
