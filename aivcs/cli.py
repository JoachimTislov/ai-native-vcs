"""aivcs CLI.

    aivcs init
    aivcs spec new <name> <file.md>
    aivcs spec show <name> [--version N]
    aivcs agent add-primitive <name> --system-prompt-file <f> [--tools Read,Edit,Write,Bash]
    aivcs agent add-compounded <name> --primitive <p> --domain <path> [--surface a,b,c]
    aivcs session run --agent <name> --prompt "..." [--spec <name>]
    aivcs log <path>
    aivcs review <session_id>
    aivcs check <session_id> --test "pytest -q"
    aivcs bisect <path> --test "pytest -q"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agents import AgentStore, CompoundedAgentSpec, PrimitiveAgentSpec
    from .bisect import bisect_path
    from .index import SessionIndex
    from .models import Contract
    from .review import render as render_review
    from .session import SessionRunner
    from .spec import SpecStore
    from .store import Store


def _root() -> Path:
    return Path.cwd()


def cmd_init(args):
    from .store import Store

    store = Store(_root(), vcs=args.vcs)
    store.init()
    (_root() / ".aivcs").mkdir(exist_ok=True)
    print(f"initialized aivcs repo at {_root()} using {store.vcs}")


def cmd_spec_new(args):
    from .spec import SpecStore

    specs = SpecStore(_root())
    content = Path(args.file).read_text()
    v = specs.new_version(args.name, content)
    print(f"spec '{args.name}' -> v{v}")


def cmd_spec_show(args):
    from .spec import SpecStore

    specs = SpecStore(_root())
    print(specs.get(args.name, args.version))


def cmd_agent_add_primitive(args):
    from .agents import AgentStore, PrimitiveAgentSpec

    store = AgentStore(_root())
    prompt = Path(args.system_prompt_file).read_text()
    tools = args.tools.split(",") if args.tools else None
    spec = PrimitiveAgentSpec(
        name=args.name,
        system_prompt=prompt,
        allowed_tools=tools or ["Read", "Edit", "Write", "Bash"],
        model=args.model,
    )
    path = store.add_primitive(spec)
    print(f"wrote {path}")


def cmd_agent_add_compounded(args):
    from .agents import AgentStore, CompoundedAgentSpec
    from .models import Contract

    store = AgentStore(_root())
    surface = args.surface.split(",") if args.surface else []
    spec = CompoundedAgentSpec(
        name=args.name,
        primitive=args.primitive,
        domain=args.domain,
        contract=Contract(domain=args.domain, surface=surface),
    )
    path = store.add_compounded(spec)
    print(f"wrote {path}")


def _read_prompt(args) -> str:
    if args.prompt is not None:
        return args.prompt

    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return data

    prompt = input("Enter session prompt: ")
    if not prompt.strip():
        raise ValueError("session prompt cannot be empty")
    return prompt


def cmd_session_run(args):
    from .session import SessionRunner

    runner = SessionRunner(_root(), provider=args.provider, vcs=args.vcs)
    prompt = _read_prompt(args)
    record = asyncio.run(
        runner.run(agent_name=args.agent, prompt=prompt, spec_name=args.spec, provider=args.provider)
    )
    print(json.dumps(record.to_dict(), indent=2))


def cmd_log(args):
    from .index import SessionIndex

    idx = SessionIndex(_root() / ".aivcs" / "index.json")
    for sid in idx.history(args.path):
        print(sid)


def cmd_review(args):
    from .review import render as render_review
    from .session import SessionRunner
    from .spec import SpecStore

    runner = SessionRunner(_root())
    specs = SpecStore(_root())
    record = runner.load_record(args.session_id)
    before = after = None
    if record.spec_name and record.spec_version:
        after = specs.get(record.spec_name, record.spec_version)
        prev = record.spec_version - 1
        if prev >= 1:
            before = specs.get(record.spec_name, prev)
    print(render_review(record, before, after))


def cmd_check(args):
    import subprocess

    from .session import SessionRunner

    runner = SessionRunner(_root())
    record = runner.load_record(args.session_id)
    result = subprocess.run(args.test, shell=True, cwd=_root(), capture_output=True, text=True)
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"{status} (exit {result.returncode})")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def cmd_bisect(args):
    from .bisect import bisect_path

    result = bisect_path(_root(), args.path, args.test)
    print(f"checked {len(result.checked)} session(s): {result.checked}")
    if result.first_bad_session:
        print(f"first bad session: {result.first_bad_session}")
    else:
        print("no failing session found in history (test passes at latest recorded session)")


def main(argv=None):
    p = argparse.ArgumentParser(prog="aivcs")
    sub = p.add_subparsers(dest="cmd", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("--vcs", default=None, help="VCS backend to use (git, hg, svn, etc.)")
    init_parser.set_defaults(func=cmd_init)

    sp = sub.add_parser("spec")
    spsub = sp.add_subparsers(dest="spec_cmd", required=True)
    s1 = spsub.add_parser("new")
    s1.add_argument("name")
    s1.add_argument("file")
    s1.set_defaults(func=cmd_spec_new)
    s2 = spsub.add_parser("show")
    s2.add_argument("name")
    s2.add_argument("--version", type=int, default=None)
    s2.set_defaults(func=cmd_spec_show)

    ap = sub.add_parser("agent")
    apsub = ap.add_subparsers(dest="agent_cmd", required=True)
    a1 = apsub.add_parser("add-primitive")
    a1.add_argument("name")
    a1.add_argument("--system-prompt-file", required=True)
    a1.add_argument("--tools", default=None)
    a1.add_argument("--model", default=None)
    a1.set_defaults(func=cmd_agent_add_primitive)
    a2 = apsub.add_parser("add-compounded")
    a2.add_argument("name")
    a2.add_argument("--primitive", required=True)
    a2.add_argument("--domain", required=True)
    a2.add_argument("--surface", default=None)
    a2.set_defaults(func=cmd_agent_add_compounded)

    se = sub.add_parser("session")
    sesub = se.add_subparsers(dest="session_cmd", required=True)
    se1 = sesub.add_parser("run")
    se1.add_argument("--agent", required=True)
    se1.add_argument("--prompt", default=None)
    se1.add_argument("--spec", default=None)
    se1.add_argument("--provider", default=None, help="AI provider backend (claude, copilot, openai, gemini, ollama, auto)")
    se1.add_argument("--vcs", default=None, help="VCS backend to use (git, hg, svn, etc.)")
    se1.set_defaults(func=cmd_session_run)

    lg = sub.add_parser("log")
    lg.add_argument("path")
    lg.set_defaults(func=cmd_log)

    rv = sub.add_parser("review")
    rv.add_argument("session_id")
    rv.set_defaults(func=cmd_review)

    ck = sub.add_parser("check")
    ck.add_argument("session_id")
    ck.add_argument("--test", required=True)
    ck.set_defaults(func=cmd_check)

    bs = sub.add_parser("bisect")
    bs.add_argument("path")
    bs.add_argument("--test", required=True)
    bs.set_defaults(func=cmd_bisect)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
