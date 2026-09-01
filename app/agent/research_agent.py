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
from app.tools.fetch import fetch_source
from app.tools.search import web_search


class ResearchAgent:
    """Simple research agent that forwards a query to an LLM.

    Parameters
    ----------
    model: str, optional
        Identifier of the language model to use. Defaults to the free
        OpenRouter model ``"openrouter/free"`` so the project works with the
        free-tier provider options.
    provider: str | None, optional
        Explicit provider name (e.g., ``"ollama"``). If omitted the function
        falls back to the ``LLM_PROVIDER`` environment variable or the
        built‑in default.
    """

    def __init__(self, model: str = "openrouter/free", provider: Optional[str] = None):
        # The LLM abstraction handles provider selection and endpoint config.
        self.llm = get_llm(model=model, provider=provider)

    def _run_web_tools(self, query: str):
        """Run the search/fetch tools when the prompt needs live web grounding."""
        results = web_search(query, max_results=3)
        if not results:
            return []

        sources = []
        for result in results:
            url = result.get("url")
            if not url:
                continue
            try:
                source = fetch_source(url)
                sources.append({
                    "title": source.title,
                    "url": str(source.url),
                    "snippet": source.content[:600] if source.content else result.get("snippet", ""),
                })
            except Exception:
                sources.append(result)
        return sources

    def ask(self, query: str) -> str:
        """Send *query* to the LLM and return its answer.

        The underlying LLM implements a ``generate`` method that accepts a
        single‑prompt string and returns the model's textual completion.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non‑empty string")

        if any(word in query.lower() for word in ["what is", "who is", "when did", "where is", "how does", "latest", "news", "compare", "explain", "research", "define"]):
            sources = self._run_web_tools(query)
            if sources:
                context = "\n\n".join(
                    f"Source: {item['title']}\nURL: {item['url']}\nContent: {item['snippet']}"
                    for item in sources
                )
                enhanced_prompt = (
                    "Use the web sources below to answer the user's question. "
                    "Cite the source material, and if the sources disagree, say so.\n\n"
                    f"Question: {query}\n\nSources:\n{context}"
                )
                return self.llm.generate(enhanced_prompt)

        return self.llm.generate(query)
