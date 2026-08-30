"""Core object model.

These are plain, serializable dataclasses. Nothing here talks to git or the
Claude Agent SDK directly — that's store.py / session.py's job — so the
shapes here stay stable even as the runtime pieces change.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Contract:
    """The interface boundary a domain exposes.

    Conflicts are checked against this, not against files or lines: if two
    sessions touch the same domain but neither changes anything listed in
    `surface`, they are not in conflict.
    """

    domain: str
    surface: list[str] = field(default_factory=list)  # e.g. function signatures, route paths
    version: int = 1
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Contract":
        return cls(**d)


@dataclass
class Ambiguity:
    """One ambiguity a session resolved, and how — feeds the review artifact."""

    description: str
    resolution: str


@dataclass
class SessionRecord:
    """A completed session: the atomic unit that produced or modified an
    implementation. This is what the index tracks per file/folder, and what
    bisection replays.
    """

    session_id: str
    domain: str
    agent: str
    prompt: str
    spec_name: Optional[str]
    spec_version: Optional[int]
    commit_sha: str
    parent_sha: Optional[str]
    changed_paths: list[str]
    ambiguities: list[Ambiguity] = field(default_factory=list)
    tests_newly_passing: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SessionRecord":
        d = dict(d)
        d["ambiguities"] = [Ambiguity(**a) for a in d.get("ambiguities", [])]
        return cls(**d)
