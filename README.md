# Research Agent

A **minimal research agent** that forwards a user query to a language model (LLM) and returns the model's answer. It can be used directly from Python code or as a sub‑agent in larger workflows, and includes a simple command‑line interface (CLI) powered by **Typer**.

## Features

- **Simple workflow** – `User Query → LLM → Answer`.
- **Provider‑agnostic** – Uses the existing LLM abstraction (`app.LLM.get_llm`). By default, it talks to an Ollama server, but any provider that implements the `LLMBase` interface can be swapped in via the `LLM_PROVIDER` environment variable.
- **Library and CLI** – Use the `ResearchAgent` class in your own Python code, or run `python -m app.agent.cli ask "<question>"` from the terminal.
- **Extensible** – Designed to be a building block for more complex agents; the `ask` method can be wrapped or combined with other tools.

## Quick start (library)

```python
from app.agent import ResearchAgent

# Create an agent – model name defaults to a capable Claude model.
agent = ResearchAgent(model="gpt-oss:120b-cloud")

# Ask a question.
answer = agent.ask("What are the health benefits of regular exercise?")
print(answer)
```

## Quick start (CLI)

```bash
# Activate the virtual environment if you have one.
source venv/bin/activate

# Run the CLI – the command is `ask` followed by the query.
python -m app.agent.cli ask "Explain quantum entanglement in simple terms."
```

You can override the model or provider with the optional flags:

```bash
python -m app.agent.cli ask "..." --model "gpt-oss:120b-cloud" --provider ollama
```

## Architecture

- **LLM abstraction** – Defined in `app/LLM`. The `get_llm` factory creates a concrete LLM instance based on the `LLM_PROVIDER` environment variable (defaults to Ollama).
- **Data models** – Pydantic models in `app/models` describe evidence, sources, research projects, and tasks. They are reusable across the codebase.
- **ResearchAgent** – Thin wrapper (`app/agent/research_agent.py`) that obtains an LLM and delegates query handling to its `generate` method.
- **CLI** – `app/agent/cli.py` uses Typer to expose a single `ask` command.

## Installation

```bash
# Clone the repository (if you haven't already).
git clone <repo-url>
cd "research agent"

# Create a virtual environment.
python3 -m venv venv
source venv/bin/activate

# Install dependencies.
pip install -r requirements.txt
```

> **Note:** The agent assumes an Ollama server is running at `http://localhost:11434`. Set the `OLLAMA_ENDPOINT` environment variable if your server uses a different address, or set `LLM_PROVIDER` to another supported provider.

## Extending the agent

If you need richer interaction (e.g., multi‑turn chat), extend the `ResearchAgent` with a `chat(messages: list[dict]) -> str` method that forwards the list to `self.llm.chat(messages)`. The underlying LLM abstraction already supports that.

---

*Generated with Claude Code*