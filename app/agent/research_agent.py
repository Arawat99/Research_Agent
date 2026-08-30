"""Minimal research agent.

The ``ResearchAgent`` class provides the most straightforward workflow
required for a research‑assistant style tool: a user supplies a natural‑language
query, the agent forwards the query to a configured language model, and the
model's answer is returned.

The implementation builds on the project's LLM abstraction (`app.LLM`). By
default it uses the model ``gpt-oss:120b-cloud`` and the provider resolved from
the ``LLM_PROVIDER`` environment variable (``ollama`` by default). The design
keeps the agent deliberately small so it can serve as a sub‑agent in larger
or more complex pipelines without pulling in unnecessary dependencies.
"""

from __future__ import annotations

from typing import Optional

from app.LLM import get_llm


class ResearchAgent:
    """Simple research agent that forwards a query to an LLM.

    Parameters
    ----------
    model: str, optional
        Identifier of the language model to use. Defaults to
        ``"gpt-oss:120b-cloud"`` which resolves to a high‑capacity Claude model
        when the ``claude‑code`` environment is available.
    provider: str | None, optional
        Explicit provider name (e.g., ``"ollama"``). If omitted the function
        falls back to the ``LLM_PROVIDER`` environment variable or the
        built‑in default.
    """

    def __init__(self, model: str = "gpt-oss:120b-cloud", provider: Optional[str] = None):
        # The LLM abstraction handles provider selection and endpoint config.
        self.llm = get_llm(model=model, provider=provider)

    def ask(self, query: str) -> str:
        """Send *query* to the LLM and return its answer.

        The underlying LLM implements a ``generate`` method that accepts a
        single‑prompt string and returns the model's textual completion.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non‑empty string")
        return self.llm.generate(query)
