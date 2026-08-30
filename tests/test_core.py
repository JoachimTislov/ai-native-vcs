import json
import subprocess
import uuid
from pathlib import Path

import pytest

from aivcs.store import Store
from aivcs.index import SessionIndex
from aivcs.spec import SpecStore
from aivcs.models import SessionRecord, Ambiguity
from aivcs.bisect import bisect_path


@pytest.fixture
def repo(tmp_path):
    store = Store(tmp_path)
    store.init()
    return tmp_path, store


def _fake_session(root: Path, store: Store, idx: SessionIndex, files: dict, msg: str) -> str:
    parent = store.head()
    for path, content in files.items():
        (root / path).write_text(content)
    sid = str(uuid.uuid4())
    sha = store.commit_all(f"session:{sid} {msg}")
    changed = store.changed_paths(sha, parent=parent)
    idx.append_many(changed, sid)
    idx.save()
    sessions_dir = root / ".aivcs" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    rec = SessionRecord(
        session_id=sid, domain="d", agent="a", prompt=msg, spec_name=None,
        spec_version=None, commit_sha=sha, parent_sha=parent, changed_paths=changed,
    )
    (sessions_dir / f"{sid}.json").write_text(json.dumps(rec.to_dict()))
    return sid


def test_store_init_creates_root_commit(repo):
    root, store = repo
    assert store.head() is not None


def test_commit_all_dedups_identical_content(repo):
    root, store = repo
    (root / "a.txt").write_text("same")
    (root / "b.txt").write_text("same")
    sha = store.commit_all("two identical files")
    r = subprocess.run(["git", "-C", str(root), "cat-file", "-p", f"{sha}^{{tree}}"],
                        capture_output=True, text=True)
    assert r.returncode == 0


def test_index_append_only_and_ordered(repo):
    root, store = repo
    idx = SessionIndex(root / ".aivcs" / "index.json")
    s1 = _fake_session(root, store, idx, {"f.txt": "v1"}, "s1")
    s2 = _fake_session(root, store, idx, {"f.txt": "v2"}, "s2")
    assert idx.history("f.txt") == [s1, s2]


def test_spec_versions_are_never_overwritten(tmp_path):
    specs = SpecStore(tmp_path)
    v1 = specs.new_version("dom", "first")
    v2 = specs.new_version("dom", "second")
    assert (v1, v2) == (1, 2)
    assert specs.get("dom", 1) == "first"
    assert specs.get("dom", 2) == "second"
    assert specs.get("dom") == "second"  # latest by default


def test_bisect_finds_exact_regressing_session(repo):
    root, store = repo
    idx = SessionIndex(root / ".aivcs" / "index.json")
    _fake_session(
        root, store, idx,
        {"m.py": "def add(a, b):\n    return a + b\n",
         "test_m.py": "from m import add\ndef test_add():\n    assert add(2, 3) == 5\n"},
        "implement",
    )
    _fake_session(root, store, idx, {"m.py": "def add(a, b):\n    return a + b  # noop change\n"}, "cosmetic")
    bad_sid = _fake_session(root, store, idx, {"m.py": "def add(a, b):\n    return a - b\n"}, "regression")

    result = bisect_path(root, "m.py", "python -m pytest test_m.py -q")
    assert result.first_bad_session == bad_sid


def test_bisect_returns_none_when_history_never_fails(repo):
    root, store = repo
    idx = SessionIndex(root / ".aivcs" / "index.json")
    _fake_session(
        root, store, idx,
        {"m.py": "def add(a, b):\n    return a + b\n",
         "test_m.py": "from m import add\ndef test_add():\n    assert add(2, 3) == 5\n"},
        "implement",
    )
    result = bisect_path(root, "m.py", "python -m pytest test_m.py -q")
    assert result.first_bad_session is None
