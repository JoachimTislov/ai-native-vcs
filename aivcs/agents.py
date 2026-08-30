"""Primitive agent specs and compounded agents.

"Primitive agent spec — base definition that specialized agents compound
from; acts like a base image (a flaw here propagates to every agent built
on it). Compounded agent — a specialized agent scoped to a specific
contract and domain, built on top of a primitive spec."

A primitive spec is shared, general instructions + a default toolset. A
compounded agent inherits a primitive by name and narrows it to one domain
and one contract. This maps directly onto Claude Agent SDK subagents: a
compounded agent becomes a `ClaudeAgentOptions` (system prompt + allowed
tools + cwd) scoped to a slice of the repo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .models import Contract


@dataclass
class PrimitiveAgentSpec:
    name: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=lambda: ["Read", "Edit", "Write", "Bash"])
    model: Optional[str] = None  # None -> SDK default


@dataclass
class CompoundedAgentSpec:
    name: str
    primitive: str
    domain: str            # path/glob this agent owns
    contract: Contract
    extra_instructions: str = ""


class AgentStore:
    def __init__(self, root: Path):
        self.root = Path(root) / "agents"
        self.primitive_dir = self.root / "primitive"
        self.compounded_dir = self.root / "compounded"

    def add_primitive(self, spec: PrimitiveAgentSpec) -> Path:
        self.primitive_dir.mkdir(parents=True, exist_ok=True)
        p = self.primitive_dir / f"{spec.name}.yaml"
        p.write_text(yaml.safe_dump({
            "name": spec.name,
            "system_prompt": spec.system_prompt,
            "allowed_tools": spec.allowed_tools,
            "model": spec.model,
        }, sort_keys=False))
        return p

    def load_primitive(self, name: str) -> PrimitiveAgentSpec:
        d = yaml.safe_load((self.primitive_dir / f"{name}.yaml").read_text())
        return PrimitiveAgentSpec(**d)

    def add_compounded(self, spec: CompoundedAgentSpec) -> Path:
        self.compounded_dir.mkdir(parents=True, exist_ok=True)
        p = self.compounded_dir / f"{spec.name}.yaml"
        p.write_text(yaml.safe_dump({
            "name": spec.name,
            "primitive": spec.primitive,
            "domain": spec.domain,
            "contract": spec.contract.to_dict(),
            "extra_instructions": spec.extra_instructions,
        }, sort_keys=False))
        return p

    def load_compounded(self, name: str) -> CompoundedAgentSpec:
        d = yaml.safe_load((self.compounded_dir / f"{name}.yaml").read_text())
        return CompoundedAgentSpec(
            name=d["name"],
            primitive=d["primitive"],
            domain=d["domain"],
            contract=Contract.from_dict(d["contract"]),
            extra_instructions=d.get("extra_instructions", ""),
        )

    def build_system_prompt(self, compounded_name: str, spec_text: str = "") -> tuple[str, list[str], Optional[str]]:
        """Resolve a compounded agent + its primitive into a ready-to-run
        (system_prompt, allowed_tools, model) tuple.
        """
        comp = self.load_compounded(compounded_name)
        prim = self.load_primitive(comp.primitive)
        parts = [
            prim.system_prompt,
            f"\nYou are scoped to the domain: {comp.domain}",
            f"Its contract surface (do not break these without flagging it): {comp.contract.surface}",
        ]
        if comp.extra_instructions:
            parts.append(comp.extra_instructions)
        if spec_text:
            parts.append("\n--- Specification you must implement ---\n" + spec_text)
        parts.append(
            "\nIf you resolve any ambiguity in the spec, say so explicitly in your "
            "final message as a line starting with 'AMBIGUITY:' followed by what you "
            "resolved and how — this feeds the review artifact."
        )
        return "\n".join(parts), prim.allowed_tools, prim.model
