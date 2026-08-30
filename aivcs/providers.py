from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProviderPlan:
    name: str
    supports_resume: bool = False
    default_model: Optional[str] = None
    cli: Optional[str] = None


def normalize_provider(provider: Optional[str]) -> str:
    if provider is None:
        return "auto"
    value = provider.strip().lower()
    aliases = {
        "claude": "claude",
        "anthropic": "claude",
        "claude-code": "claude",
        "claude-cli": "claude",
        "copilot": "copilot",
        "github-copilot": "copilot",
        "gh-copilot": "copilot",
        "copilot-cli": "copilot",
        "openai": "openai",
        "gpt": "openai",
        "gpt4": "openai",
        "gpt-4": "openai",
        "chatgpt": "openai",
        "gemini": "gemini",
        "google-gemini": "gemini",
        "gemini-cli": "gemini",
        "ollama": "ollama",
        "local": "local",
        "auto": "auto",
    }
    return aliases.get(value, value)


def detect_provider(provider: Optional[str] = None) -> ProviderPlan:
    name = normalize_provider(provider or os.getenv("AIVCS_PROVIDER"))
    if name == "auto":
        for cli_name in ("claude", "copilot", "openai", "gemini", "ollama"):
            if shutil.which(cli_name):
                # Normalize the CLI's provider name when a concrete tool is on PATH.
                return resolve_provider(cli_name)
        return ProviderPlan(name="auto", supports_resume=False, default_model=None, cli=None)
    return resolve_provider(name)


def resolve_provider(provider: Optional[str]) -> ProviderPlan:
    name = normalize_provider(provider)
    if name in {"claude", "anthropic"}:
        return ProviderPlan(name="claude", supports_resume=True, default_model=None, cli="claude")
    if name in {"copilot", "github-copilot", "gh-copilot"}:
        return ProviderPlan(name="copilot", supports_resume=True, default_model=None, cli="copilot")
    if name in {"openai", "gpt", "chatgpt", "gpt4", "gpt-4"}:
        return ProviderPlan(name="openai", supports_resume=False, default_model=None, cli="openai")
    if name in {"gemini", "google-gemini"}:
        return ProviderPlan(name="gemini", supports_resume=False, default_model=None, cli="gemini")
    if name == "ollama":
        return ProviderPlan(name="ollama", supports_resume=False, default_model=None, cli="ollama")
    if name == "local":
        return ProviderPlan(name="local", supports_resume=False, default_model=None, cli=None)
    if name == "auto":
        return ProviderPlan(name="auto", supports_resume=False, default_model=None, cli=None)
    return ProviderPlan(name=name, supports_resume=False, default_model=None, cli=name)
