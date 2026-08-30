#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "SPEC_LIST.md"

REQUIRED = {
    "status:planned",
    "status:in-progress",
    "status:done",
    "area:core",
    "area:spec",
    "area:docs",
    "area:workflow",
    "area:release",
    "priority:low",
    "priority:medium",
    "priority:high",
    "type:feature",
    "type:spec",
    "type:research",
    "type:task",
}


def run_gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh command failed")
    return proc.stdout


def issue_numbers_from_spec() -> set[int]:
    text = SPEC.read_text(encoding="utf-8")
    return {int(v) for v in re.findall(r"#(\d+)", text)}


def detect_area(title: str, body: str) -> str:
    haystack = f"{title}\n{body}".lower()
    if any(k in haystack for k in ["spec", "architecture", "agent", "contract", "session", "history", "git", "bisect", "review", "design"]):
        return "area:core"
    if any(k in haystack for k in ["readme", "doc", "guide", "contributing", "policy", "template"]):
        return "area:docs"
    if any(k in haystack for k in ["workflow", "ci", "action", "issue", "automation", "branch", "commit", "label"]):
        return "area:workflow"
    if any(k in haystack for k in ["release", "version", "binary", "package", "npm", "artifact"]):
        return "area:release"
    return "area:spec"


def detect_type(title: str, body: str) -> str:
    haystack = f"{title}\n{body}".lower()
    if any(k in haystack for k in ["evaluate", "research", "investigate", "explore", "analysis"]):
        return "type:research"
    if any(k in haystack for k in ["feature", "plugin", "distribution", "package", "add", "implement"]):
        return "type:feature"
    if any(k in haystack for k in ["spec", "architecture", "design"]):
        return "type:spec"
    return "type:task"


def detect_priority(title: str, body: str) -> str:
    haystack = f"{title}\n{body}".lower()
    if any(k in haystack for k in ["urgent", "critical", "high", "priority"]):
        return "priority:high"
    if any(k in haystack for k in ["medium", "normal", "moderate"]):
        return "priority:medium"
    return "priority:low"


def main() -> int:
    issues = json.loads(run_gh(["issue", "list", "--state", "all", "--limit", "200", "--json", "number,title,body,labels"]))
    spec_numbers = issue_numbers_from_spec()
    changed = 0

    for issue in issues:
        labels = {label["name"] for label in issue.get("labels", [])}
        title = issue.get("title", "")
        body = issue.get("body") or ""
        num = issue["number"]
        origin = "ai" if any(label in {"ai", "ai-generated"} for label in labels) else "human"
        labels.discard("ai")
        labels.discard("human")
        labels.discard("ai-generated")
        labels.discard("human-generated")
        labels.discard("status:planned")
        labels.discard("status:in-progress")
        labels.discard("status:done")
        labels.discard("area:core")
        labels.discard("area:spec")
        labels.discard("area:docs")
        labels.discard("area:workflow")
        labels.discard("area:release")
        labels.discard("priority:low")
        labels.discard("priority:medium")
        labels.discard("priority:high")
        labels.discard("type:feature")
        labels.discard("type:spec")
        labels.discard("type:research")
        labels.discard("type:task")

        status = "status:done" if num in spec_numbers and any(f"- [x]" in line for line in SPEC.read_text(encoding="utf-8").splitlines()) else "status:planned"
        if "#%s" % num in SPEC.read_text(encoding="utf-8") and "- [ ]" in SPEC.read_text(encoding="utf-8"):
            status = "status:planned"
        labels.add(origin)
        labels.add(status)
        labels.add(detect_area(title, body))
        labels.add(detect_priority(title, body))
        labels.add(detect_type(title, body))

        if labels - REQUIRED:
            pass

        expected = sorted(labels)
        current = sorted(label["name"] for label in issue.get("labels", []))
        if current != expected:
            changed += 1
            label_list = sorted(labels)
            subprocess.run(["gh", "issue", "edit", str(num), "--add-label", ",".join(label_list)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"synced issue #{num}: {sorted(label_list)}")

    if changed == 0:
        print("Issue label sync: clean")
        return 0
    print(f"Issue label sync: updated {changed} issue(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"issue_label_sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
