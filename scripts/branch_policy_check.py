#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys

pattern = re.compile(r"^(main|master|develop|release|hotfix|feature|fix|chore|docs|refactor|test|ci)/[a-z0-9._/-]+$")
branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or os.environ.get("BRANCH_NAME")

if not branch:
    print("No branch name provided; skipping branch policy check.")
    sys.exit(0)

if branch in {"main", "master", "develop"}:
    print(f"Branch '{branch}' is allowed.")
    sys.exit(0)

if not pattern.match(branch):
    print(f"Branch name '{branch}' does not match the required naming convention.")
    print("Use: <type>/<short-name>, for example feature/auth-flow, fix/checkout-rounding, chore/release-prep")
    sys.exit(1)

print(f"Branch '{branch}' passes the naming policy.")
