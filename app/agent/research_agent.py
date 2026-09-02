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
from app.LLM.openrouter import OpenRouterError
from app.agent.planner import ResearchPlanner
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

        Returns a list of normalized source dictionaries so the queue-driven
        research loop can accumulate evidence until it is sufficient.
        """
        search_result = web_search(query, max_results=3)
        if isinstance(search_result, dict):
            results = search_result.get("results") or []
        else:
            results = search_result or []

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
            except httpx.ConnectError:
                sources.append(result)
            except httpx.TimeoutException:
                sources.append(result)
            except Exception:
                sources.append(result)
        return sources

    def _evidence_is_sufficient(self, sources: list[dict], min_sources: int = 2) -> bool:
        """Return True only when there is enough material to answer the question reliably."""
        if len(sources) < min_sources:
            return False
        return any((item.get("snippet") or "").strip() for item in sources)

    def _safe_generate(self, prompt: str) -> str:
        """Generate a completion with a safe fallback when the provider is empty or malformed."""
        try:
            return self.llm.generate(prompt)
        except OpenRouterError as exc:
            return (
                "I could not get a valid model response from the configured provider. "
                f"The provider returned an empty or malformed payload: {exc}"
            )
        except Exception as exc:
            return (
                "I could not complete the model call due to a provider failure. "
                f"Details: {exc}"
            )

    def _finalize_answer(self, query: str, sources: list[dict]) -> str:
        """Ask the LLM to answer once the evidence threshold has been reached."""
        if not sources:
            return self.ask(query)

        context = "\n\n".join(
            f"Source: {item['title']}\nURL: {item['url']}\nContent: {item['snippet']}"
            for item in sources
        )
        prompt = (
            "=== USER QUERY ===\n"
            f"{query}\n\n"
            "=== COLLECTED EVIDENCE ===\n"
            f"{context}\n\n"
            "=== TASK ===\n"
            "Answer the user's question using the evidence above. "
            "If the evidence is weak or incomplete, say so clearly. "
            "Cite the source material and explain any uncertainty."
        )
        return self._safe_generate(prompt)

    def research(
        self,
        query: str,
        max_rounds: int = 3,
        min_sources: int = 2,
        num_tasks: int = 3,
    ) -> str:
        """Perform iterative research with a task queue until enough evidence is found."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")

        planner = ResearchPlanner(model="openrouter/free")
        tasks = planner.create_plan(query, num_tasks=num_tasks)
        queue = TaskQueue(tasks)
        collected_sources: list[dict] = []
        rounds_without_new_evidence = 0

        for _ in range(max_rounds):
            if not queue.has_pending():
                break

            task = queue.next_ready()
            if task is None:
                break

            new_sources = self._run_web_tools(task.question)
            if new_sources:
                collected_sources.extend(new_sources)
                rounds_without_new_evidence = 0
            else:
                rounds_without_new_evidence += 1

            queue.mark_completed(task)

            if self._evidence_is_sufficient(collected_sources, min_sources=min_sources):
                return self._finalize_answer(query, collected_sources)

            if rounds_without_new_evidence >= 2:
                break

        if collected_sources:
            return self._finalize_answer(query, collected_sources)

        return self.ask(query)

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
                    "=== USER QUERY ===\n"
                    f"{query}\n\n"
                    "=== AGENT WEB SEARCH RESULTS ===\n"
                    "(The following sources were automatically retrieved by the agent's web search tools, NOT provided by the user)\n\n"
                    f"{context}\n\n"
                    "=== TASK ===\n"
                    "Use the web search results above to answer the user's query. "
                    "Cite specific sources when providing information. "
                    "If the sources conflict, acknowledge the disagreement. "
                    "Do NOT treat these web results as user-provided information."
                )
                return self._safe_generate(enhanced_prompt)

            no_sources_prompt = (
                "=== USER QUERY ===\n"
                f"{query}\n\n"
                "=== AGENT WEB SEARCH STATUS ===\n"
                "The agent attempted to perform a web search but did not retrieve usable sources.\n\n"
                "=== TASK ===\n"
                "Answer the user's question based on your training data and note the lack of dependable web evidence."
            )
            return self._safe_generate(no_sources_prompt)

        return self._safe_generate(query)

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
