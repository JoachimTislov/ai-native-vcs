"""Session runner.

"Session — a bound unit of execution (session ID) carrying full context;
the atomic thing that produces or modifies an implementation."

A session here = one Claude Agent SDK `query()` run, scoped by a compounded
agent's system prompt/tools/domain, given the current Specification text as
context. When it finishes, the working tree is committed as one snapshot
(store.commit_all), the session index is updated for every path that
changed, and a SessionRecord + review-artifact stub are written to disk.

Requires `pip install claude-agent-sdk` and an ANTHROPIC_API_KEY in the
environment to actually call the model. Everything else in this package
(store, index, spec, bisect, cli) works without it — this is the one module
with a live-API dependency, kept isolated on purpose.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Optional

from .agents import AgentStore
from .index import SessionIndex
from .models import Ambiguity, SessionRecord
from .spec import SpecStore
from .store import Store


AMBIGUITY_RE = re.compile(r"^AMBIGUITY:\s*(.+)$", re.MULTILINE)


class SessionRunner:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.store = Store(self.root)
        self.index = SessionIndex(self.root / ".aivcs" / "index.json")
        self.agents = AgentStore(self.root)
        self.specs = SpecStore(self.root)
        self.sessions_dir = self.root / ".aivcs" / "sessions"

    async def run(
        self,
        agent_name: str,
        prompt: str,
        spec_name: Optional[str] = None,
        max_turns: int = 40,
    ) -> SessionRecord:
        from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock

        comp = self.agents.load_compounded(agent_name)
        spec_version = self.specs.latest_version(spec_name) if spec_name else None
        spec_text = self.specs.get(spec_name, spec_version) if spec_name else ""

        system_prompt, allowed_tools, model = self.agents.build_system_prompt(agent_name, spec_text)

        parent_sha = self.store.head()
        session_id = str(uuid.uuid4())

        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            permission_mode="acceptEdits",
            cwd=str(self.root),
            model=model,
            max_turns=max_turns,
        )

        transcript_text_parts: list[str] = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        transcript_text_parts.append(block.text)
            elif isinstance(message, ResultMessage):
                if message.result:
                    transcript_text_parts.append(message.result)

        full_text = "\n".join(transcript_text_parts)
        ambiguities = [Ambiguity(description=m, resolution=m) for m in AMBIGUITY_RE.findall(full_text)]

        commit_sha = self.store.commit_all(f"session:{session_id} agent:{agent_name}")
        changed = self.store.changed_paths(commit_sha, parent=parent_sha)
        self.index.append_many(changed, session_id)
        self.index.save()

        record = SessionRecord(
            session_id=session_id,
            domain=comp.domain,
            agent=agent_name,
            prompt=prompt,
            spec_name=spec_name,
            spec_version=spec_version,
            commit_sha=commit_sha,
            parent_sha=parent_sha,
            changed_paths=changed,
            ambiguities=ambiguities,
        )
        self._save_record(record, full_text)
        return record

    def _save_record(self, record: SessionRecord, transcript_text: str) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        (self.sessions_dir / f"{record.session_id}.json").write_text(
            json.dumps(record.to_dict(), indent=2)
        )
        (self.sessions_dir / f"{record.session_id}.transcript.txt").write_text(transcript_text)

    def load_record(self, session_id: str) -> SessionRecord:
        d = json.loads((self.sessions_dir / f"{session_id}.json").read_text())
        return SessionRecord.from_dict(d)
