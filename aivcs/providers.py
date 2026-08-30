from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProviderPlan:
    name: str
    supports_resume: bool = False
    default_model: Optional[str] = None


def normalize_provider(provider: Optional[str]) -> str:
    if provider is None:
        return "auto"
    value = provider.strip().lower()
    aliases = {
        "claude": "claude",
        "anthropic": "claude",
        "copilot": "copilot",
        "github-copilot": "copilot",
        "openai": "openai",
        "gpt": "openai",
        "auto": "auto",
    }
    return aliases.get(value, value)


def resolve_provider(provider: Optional[str]) -> ProviderPlan:
    name = normalize_provider(provider)
    if name in {"claude", "anthropic"}:
        return ProviderPlan(name="claude", supports_resume=True, default_model=None)
    if name in {"copilot", "github-copilot"}:
        return ProviderPlan(name="copilot", supports_resume=True, default_model=None)
    if name in {"openai", "gpt"}:
        return ProviderPlan(name="openai", supports_resume=False, default_model=None)
    if name == "auto":
        # Prefer the explicit provider if an SDK or CLI is available; keep the
        # abstraction provider-agnostic by default.
        return ProviderPlan(name="auto", supports_resume=False, default_model=None)
    return ProviderPlan(name=name, supports_resume=False, default_model=None)
