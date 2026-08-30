#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys

pattern = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([a-z0-9._/-]+\))?: .{1,72}$"
)

# Read the range of commits for PRs or the latest HEAD on push.
if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
    base = os.environ.get("GITHUB_BASE_REF", "origin/main")
    head = os.environ.get("GITHUB_HEAD_REF", "HEAD")
    cmd = ["git", "log", f"origin/{base}..HEAD", "--pretty=%s"]
else:
    cmd = ["git", "log", "-1", "--pretty=%s"]

try:
    commits = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).splitlines()
except subprocess.CalledProcessError:
    commits = []

if not commits:
    print("No commits to validate.")
    sys.exit(0)

commits = [msg for msg in commits if msg and not re.match(r"^Merge\b", msg)]

if not commits:
    print("No non-merge commit subjects to validate.")
    sys.exit(0)

bad = [msg for msg in commits if not pattern.match(msg)]
if bad:
    print("Commit messages do not match the required conventional format.")
    for msg in bad:
        print(f" - {msg}")
    print("Use: <type>(<scope>): <summary>")
    sys.exit(1)

print("All commit subjects pass the conventional commit policy.")
