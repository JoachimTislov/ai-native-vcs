"""The session-ID index.

Per the spec: "Each file/folder stores a linear array of session IDs that
have touched it (append-only history)." This is the actual history model
users interact with — not git log. It's deliberately just a JSON file: the
point isn't performance, it's that "history" here means "which sessions
touched this," not "what changed line by line."
"""

from __future__ import annotations

import json
from pathlib import Path


class SessionIndex:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._data: dict[str, list[str]] = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text())

    def append(self, file_path: str, session_id: str) -> None:
        history = self._data.setdefault(file_path, [])
        if not history or history[-1] != session_id:
            history.append(session_id)

    def append_many(self, file_paths: list[str], session_id: str) -> None:
        for p in file_paths:
            self.append(p, session_id)

    def history(self, file_path: str) -> list[str]:
        return list(self._data.get(file_path, []))

    def paths(self) -> list[str]:
        return list(self._data.keys())

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True))
