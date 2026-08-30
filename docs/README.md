# Documentation for the Research Agent

This folder contains detailed documentation that complements the top‑level README.

## Overview (`docs/overview.md`)

- Purpose of the project.
- High‑level architecture (LLM abstraction, data models, research agent).
- How the components fit together.

## Usage (`docs/usage.md`)

- Library usage example (same as README but with step‑by‑step instructions).
- CLI usage with optional flags.
- Environment configuration (LLM provider, endpoint, model selection).

## API (`docs/api.md`)

- `ResearchAgent` class signature.
- Public methods:
  - `__init__(model: str = "gpt-oss:120b-cloud", provider: Optional[str] = None)` – creates the agent.
  - `ask(query: str) -> str` – sends the query to the LLM and returns the answer.
- Possible extensions (chat, custom prompting).

---

*Generated with Claude Code*