---
name: provider-agnostic-flow
description: Design note for provider-neutral execution across AI backends and sessions.
---

# Provider-agnostic execution model

The runtime should be provider-neutral. The repository abstracts the AI backend so the same session flow can work with Claude, Copilot, OpenAI, or future providers.

Principles:
- session history is provider-agnostic
- resume is optional and must not redefine the underlying model
- provider adapters are runtime details, not canonical design truth
