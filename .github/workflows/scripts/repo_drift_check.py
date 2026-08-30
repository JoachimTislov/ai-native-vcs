#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys


REQUIRED_STATUS = {"status:planned", "status:in-progress", "status:done"}
REQUIRED_AREA = {"area:core", "area:spec", "area:docs", "area:workflow", "area:release"}
REQUIRED_PRIORITY = {"priority:low", "priority:medium", "priority:high"}
REQUIRED_TYPE = {"type:feature", "type:spec", "type:research", "type:task"}


def gh_json(args: list[str]):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh command failed")
    return json.loads(proc.stdout)


def main() -> int:
    issues = gh_json(["issue", "list", "--state", "all", "--limit", "200", "--json", "number,title,labels"])
    drift = []
    for issue in issues:
        labels = {label["name"] for label in issue.get("labels", [])}
        if not labels & {"ai", "human"}:
            drift.append(f"#{issue['number']}: missing origin label")
        if not (labels & REQUIRED_STATUS):
            drift.append(f"#{issue['number']}: missing status label")
        if not (labels & REQUIRED_AREA):
            drift.append(f"#{issue['number']}: missing area label")
        if not (labels & REQUIRED_PRIORITY):
            drift.append(f"#{issue['number']}: missing priority label")
        if not (labels & REQUIRED_TYPE):
            drift.append(f"#{issue['number']}: missing type label")

    if drift:
        print("Issue taxonomy drift detected:")
        for item in drift:
            print(f" - {item}")
        return 1

    print("Issue taxonomy is consistent and repo drift checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"repo_drift_check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
