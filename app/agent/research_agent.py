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

from typing import Callable, Optional

import httpx

from app.LLM import get_llm
from app.agent.task_queue import TaskQueue
from app.models.task import ResearchTask, TaskStatus
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
        """Run the search/fetch tools when the prompt needs live web grounding.
        
        Returns a dict with 'sources' (list), 'error' (bool), and 'error_reason' (str).
        """
        search_result = web_search(query, max_results=3)
        
        if search_result.get("error"):
            return {
                "sources": [],
                "error": True,
                "error_reason": search_result.get("error_reason", "Unknown search error")
            }
        
        results = search_result.get("results", [])
        if not results:
            return {
                "sources": [],
                "error": True,
                "error_reason": "No search results returned from the search backend."
            }

        sources = []
        fetch_errors = []
        
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
            except httpx.ConnectError as e:
                fetch_errors.append(f"Could not fetch {url}: Network connection failed")
                sources.append(result)  # Fallback to search result snippet
            except httpx.TimeoutException as e:
                fetch_errors.append(f"Could not fetch {url}: Request timed out (timeout: 10s)")
                sources.append(result)
            except Exception as e:
                fetch_errors.append(f"Could not fetch {url}: {type(e).__name__}")
                sources.append(result)
        
        return {
            "sources": sources,
            "error": False,
            "fetch_errors": fetch_errors if fetch_errors else None,
            "error_reason": None
        }

    def ask(self, query: str) -> str:
        """Send *query* to the LLM and return its answer.

        The underlying LLM implements a ``generate`` method that accepts a
        single‑prompt string and returns the model's textual completion.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non‑empty string")

        if any(word in query.lower() for word in ["what is", "who is", "when did", "where is", "how does", "latest", "news", "compare", "explain", "research", "define"]):
            web_tools_result = self._run_web_tools(query)
            sources = web_tools_result.get("sources", [])
            error_reason = web_tools_result.get("error_reason")
            fetch_errors = web_tools_result.get("fetch_errors")
            
            if sources:
                context = "\n\n".join(
                    f"Source: {item['title']}\nURL: {item['url']}\nContent: {item['snippet']}"
                    for item in sources
                )
                error_notes = ""
                if error_reason:
                    error_notes = f"\n[SEARCH ERROR]: {error_reason}"
                if fetch_errors:
                    error_notes += f"\n[FETCH WARNINGS]: {'; '.join(fetch_errors)}"
                
                enhanced_prompt = (
                    "=== USER QUERY ===\n"
                    f"{query}\n\n"
                    "=== AGENT WEB SEARCH RESULTS ===\n"
                    "(The following sources were automatically retrieved by the agent's web search tools, NOT provided by the user)\n\n"
                    f"{context}{error_notes}\n\n"
                    "=== TASK ===\n"
                    "Use the web search results above to answer the user's query. "
                    "Cite specific sources when providing information. "
                    "If the sources conflict, acknowledge the disagreement. "
                    "Do NOT treat these web results as user-provided information."
                )
                return self.llm.generate(enhanced_prompt)
            else:
                # No sources found - include error information in prompt
                error_msg = error_reason or "Could not retrieve web sources for this query."
                no_sources_prompt = (
                    "=== USER QUERY ===\n"
                    f"{query}\n\n"
                    "=== AGENT WEB SEARCH STATUS ===\n"
                    f"The agent attempted to perform a web search but failed:\n"
                    f"[SEARCH LIMITATION]: {error_msg}\n\n"
                    f"NOTE: This is a failure of the agent's search tools, NOT information provided by the user.\n\n"
                    "=== TASK ===\n"
                    "Answer the user's question based on your training data. "
                    "Be explicit that web search was unavailable and explain why the agent's search failed. "
                    "Do NOT treat this search failure as user-provided information."
                )
                return self.llm.generate(no_sources_prompt)

        return self.llm.generate(query)

    def run_task_queue(
        self,
        tasks: list[ResearchTask],
        worker: Callable[[ResearchTask], object] | None = None,
    ) -> list[tuple[ResearchTask, object]]:
        """Process queued tasks in priority order.

        This turns the research workflow from arbitrary execution into a bounded,
        deterministic task loop: each pending task is popped from the queue,
        marked in progress, executed, and marked complete before the next task is
        considered.
        """
        queue = TaskQueue(tasks)
        results: list[tuple[ResearchTask, object]] = []
        handler = worker or (lambda task: self.ask(task.question))

        while queue.has_pending():
            task = queue.next_ready()
            if task is None:
                break
            try:
                output = handler(task)
                results.append((task, output))
                queue.mark_completed(task)
            except Exception:
                queue.mark_failed(task)
                raise

        return results
