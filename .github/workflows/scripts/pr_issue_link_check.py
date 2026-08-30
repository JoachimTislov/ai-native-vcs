#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

EVENT_PATH = Path(os.environ.get("GITHUB_EVENT_PATH", ""))
if not EVENT_PATH.exists():
    print("No GitHub event payload found; skipping PR issue link check.")
    raise SystemExit(0)

payload = json.loads(EVENT_PATH.read_text(encoding="utf-8"))
pr = payload.get("pull_request")
if not pr:
    print("No pull request payload found; skipping PR issue link check.")
    raise SystemExit(0)

text = f"{pr.get('title', '')}\n{pr.get('body', '') or ''}"
pattern = re.compile(r"(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?|related to|refs?)(?:\s+to)?\s+#\d+", re.IGNORECASE)
if pattern.search(text):
    print("PR references an issue in the required format.")
    raise SystemExit(0)

print("PR must include an issue reference such as 'Fixes #123' or 'Related to #123'.")
raise SystemExit(1)
