# API Reference

## `app.agent.research_agent.ResearchAgent`

```python
class ResearchAgent:
    """Simple research agent that forwards a query to an LLM.

    Parameters
    ----------
    model: str, optional
        Identifier of the LLM model to use. Defaults to ``"gpt-oss:120b-cloud"``.
    provider: str | None, optional
        Name of the LLM provider (e.g., ``"ollama"``). If omitted, the
        ``LLM_PROVIDER`` environment variable is consulted, falling back to
        ``"ollama"``.
    """

    def __init__(self, model: str = "gpt-oss:120b-cloud", provider: str | None = None):
        ...

    def ask(self, query: str) -> str:
        """Send *query* to the underlying LLM and return the generated answer.

        This is a thin wrapper around ``LLMBase.generate``.
        """
        ...
```

### Example

```python
from app.agent import ResearchAgent
agent = ResearchAgent()
print(agent.ask("What is the speed of light?"))
```

## CLI (`app.agent.cli`)

The CLI is built with **Typer** and exposes a single command:

```
python -m app.agent.cli ask "<question>" [--model <model>] [--provider <provider>]
```

- `ask` – Sends the supplied question to the LLM and prints the answer.
- `--model` – Optional model identifier (default ``gpt-oss:120b-cloud``).
- `--provider` – Optional provider override.

The CLI simply instantiates a `ResearchAgent` with the given options and calls its `ask` method.

---

*Generated with Claude Code*