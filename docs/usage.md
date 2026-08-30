# Usage Guide

## As a Python library

```python
from app.agent import ResearchAgent

# Initialise the agent – you can optionally specify a model name
agent = ResearchAgent(model="gpt-oss:120b-cloud")

# Ask a question and receive the answer
answer = agent.ask("What is the tallest mountain on Earth?")
print(answer)
```

The `ResearchAgent` class is deliberately tiny – it only creates an LLM instance via the project's `get_llm` factory and calls its `generate` method.

### Customising the provider

Set the environment variable `LLM_PROVIDER` to the identifier of a provider that implements the `LLMBase` interface (e.g., `ollama`, `openrouter`). For Ollama, you can also set `OLLAMA_ENDPOINT` if the server is not running on the default `http://localhost:11434`.

```bash
export LLM_PROVIDER=ollama
export OLLAMA_ENDPOINT=http://my-ollama-host:11434
```

## From the command line

The repository ships a small CLI built with **Typer**. Run it with the module‑style invocation:

```bash
# Activate your virtual environment first
source venv/bin/activate

# Ask a question via the CLI
python -m app.agent.cli ask "Explain the concept of memoization."
```

### CLI options

- `--model TEXT` – Model identifier (default: `gpt-oss:120b-cloud`).
- `--provider TEXT` – Override the provider without touching the environment.

Example with custom model:

```bash
python -m app.agent.cli ask "Describe the builder pattern." --model "claude-sonnet-5"
```

## Running the tests (future work)

Currently no automated tests exist for the agent, but you can quickly sanity‑check the implementation:

```bash
python - <<'PY'
from app.agent import ResearchAgent
agent = ResearchAgent()
print(agent.ask('What is the capital of Japan?'))
PY
```

If the LLM server is reachable, you should see a sensible answer.

---

*Generated with Claude Code*