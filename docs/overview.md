# Overview

The **Research Agent** is a lightweight, extensible component that implements the classic `User Query → LLM → Answer` workflow. It leverages the project's existing LLM abstraction (`app.LLM`) which currently ships with an Ollama provider but can be extended to other back‑ends.

### Core Components

| Component | Description |
|-----------|-------------|
| **LLM abstraction** (`app/LLM`) | Provides a unified `LLMBase` interface and a `get_llm` factory that returns a concrete provider instance based on environment configuration. |
| **Data models** (`app/models`) | Pydantic models (`Evidence`, `Research`, `Source`, `ResearchTask`) representing the structured knowledge the agent can work with. |
| **ResearchAgent** (`app/agent/research_agent.py`) | Thin wrapper that creates an LLM instance and forwards a user's query to the model via `generate`. |
| **CLI** (`app/agent/cli.py`) | Simple command‑line interface built with Typer for interactive use. |

The design intentionally keeps the agent minimal so it can be imported as a sub‑agent in larger workflows without pulling in unnecessary dependencies.

---

*Generated with Claude Code*