from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


class VCSRuntimeError(RuntimeError):
    pass


class GitError(VCSRuntimeError):
    pass


class VCSPlan:
    def __init__(self, name: str, cli: str, *, supports_resume: bool = False):
        self.name = name
        self.cli = cli
        self.supports_resume = supports_resume


def normalize_vcs(vcs: Optional[str]) -> str:
    if vcs is None:
        return "auto"
    value = vcs.strip().lower()
    aliases = {
        "git": "git",
        "github": "git",
        "hg": "hg",
        "mercurial": "hg",
        "svn": "svn",
        "subversion": "svn",
        "bzr": "bzr",
        "bazaar": "bzr",
        "fossil": "fossil",
        "darcs": "darcs",
        "auto": "auto",
    }
    return aliases.get(value, value)


def detect_vcs(vcs: Optional[str] = None) -> VCSPlan:
    name = normalize_vcs(vcs)
    if name == "auto":
        for cli_name in ("git", "hg", "svn", "bzr", "fossil"):
            if shutil.which(cli_name):
                return VCSPlan(cli_name, cli_name)
        raise VCSRuntimeError("no supported VCS CLI tool found on PATH (tried git, hg, svn, bzr, fossil)")
    if name in {"git", "github"}:
        return VCSPlan("git", "git")
    if name in {"hg", "mercurial"}:
        return VCSPlan("hg", "hg")
    if name in {"svn", "subversion"}:
        return VCSPlan("svn", "svn")
    if name in {"bzr", "bazaar"}:
        return VCSPlan("bzr", "bzr")
    if name == "fossil":
        return VCSPlan("fossil", "fossil")
    if name == "darcs":
        return VCSPlan("darcs", "darcs")
    raise VCSRuntimeError(f"unsupported VCS '{vcs}'")


class VCSBackend:
    def __init__(self, root: Path, plan: Optional[VCSPlan] = None):
        self.root = Path(root)
        self.plan = plan or VCSPlan("git", "git")

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [self.plan.cli, "-C", str(self.root), *args] if self.plan.cli == "git" else [self.plan.cli, *args],
            capture_output=True,
            text=True,
            cwd=str(self.root),
        )
        if check and result.returncode != 0:
            raise GitError(f"{self.plan.cli} {' '.join(args)} failed: {result.stderr.strip()}")
        return result

    def init(self) -> None:  # pragma: no cover - interface only
        raise NotImplementedError

    def head(self) -> Optional[str]:
        raise NotImplementedError

    def commit_all(self, message: str) -> str:
        raise NotImplementedError

    def changed_paths(self, sha: str, parent: Optional[str] = None) -> list[str]:
        raise NotImplementedError

    def checkout(self, sha: str) -> None:
        raise NotImplementedError

    def checkout_ref(self, ref: str = "HEAD") -> None:
        raise NotImplementedError


class GitBackend(VCSBackend):
    def __init__(self, root: Path):
        super().__init__(root, VCSPlan("git", "git"))

    def _ensure_git_identity(self) -> None:
        if self._run(["config", "user.name"], check=False).stdout.strip() == "":
            self._run(["config", "user.name", "AIVCS Bot"])
        if self._run(["config", "user.email"], check=False).stdout.strip() == "":
            self._run(["config", "user.email", "aivcs@local.invalid"])

    def init(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._run(["init", "-q"])
        self._ensure_git_identity()
        if self._run(["log", "-1"], check=False).returncode != 0:
            self._run(["commit", "--allow-empty", "-q", "-m", "aivcs: init"])

    def head(self) -> Optional[str]:
        result = self._run(["rev-parse", "HEAD"], check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def commit_all(self, message: str) -> str:
        self._ensure_git_identity()
        self._run(["add", "-A"])
        self._run(["commit", "-q", "--allow-empty", "-m", message])
        return self.head()

    def changed_paths(self, sha: str, parent: Optional[str] = None) -> list[str]:
        base = parent or f"{sha}^"
        result = self._run(["diff", "--name-only", base, sha], check=False)
        if result.returncode != 0:
            result = self._run(["ls-tree", "-r", "--name-only", sha])
        return [p for p in result.stdout.splitlines() if p]

    def checkout(self, sha: str) -> None:
        self._run(["checkout", "-q", sha, "--", "."])

    def checkout_ref(self, ref: str = "HEAD") -> None:
        self._run(["checkout", "-q", ref])


class MercurialBackend(VCSBackend):
    def __init__(self, root: Path):
        super().__init__(root, VCSPlan("hg", "hg"))

    def init(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._run(["init", str(self.root)])

    def head(self) -> Optional[str]:
        result = self._run(["log", "-r", ".", "-T", "{node}\n"], check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def commit_all(self, message: str) -> str:
        self._run(["addremove"])
        self._run(["commit", "-m", message])
        return self.head()

    def changed_paths(self, sha: str, parent: Optional[str] = None) -> list[str]:
        if parent is None:
            result = self._run(["status", "-A", "-m", "-n"], check=False)
            return [line.split(" ", 1)[-1].strip() for line in result.stdout.splitlines() if line]
        result = self._run(["diff", "-r", parent, "-r", sha, "--stat"], check=False)
        files = []
        for line in result.stdout.splitlines():
            if "|" in line and not line.startswith("diff"):
                files.append(line.split("|", 1)[0].strip())
        return files

    def checkout(self, sha: str) -> None:
        self._run(["update", "-r", sha])

    def checkout_ref(self, ref: str = "HEAD") -> None:
        self._run(["update", "-r", ref])


def create_vcs_backend(root: Path, vcs: Optional[str] = None) -> VCSBackend:
    plan = detect_vcs(vcs)
    if plan.name == "git":
        return GitBackend(root)
    if plan.name == "hg":
        return MercurialBackend(root)
    raise VCSRuntimeError(f"unsupported VCS backend '{plan.name}'")
