"""Orchestrate planning, source collection, task execution, and synthesis."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from app.agent.answer_generator import LLMAnswerGenerator
from app.agent.interfaces import AnswerGenerator, Planner, SourceCollector
from app.agent.planner import ResearchPlanner
from app.agent.source_collector import WebSourceCollector
from app.agent.task_queue import TaskQueue
from app.models.task import ResearchTask, TaskStatus


class ResearchAgent:
    """Coordinate the research workflow without owning individual capabilities."""

    def __init__(
        self,
        model: str = "openrouter/free",
        provider: str | None = None,
        *,
        planner: Planner | None = None,
        source_collector: SourceCollector | None = None,
        answer_generator: AnswerGenerator | None = None,
    ):
        self.planner = planner or ResearchPlanner(model=model, provider=provider)
        self.source_collector = source_collector or WebSourceCollector()
        self.answer_generator = answer_generator or LLMAnswerGenerator(model=model, provider=provider)

        # Keep ``llm`` for backwards compatibility with existing integrations/tests.
        self.llm = getattr(self.answer_generator, "llm", None)

    def _report(self, callback: Callable[[dict], None] | None, event: str, **details: object) -> None:
        if callback is not None:
            callback({"event": event, **details})

    @staticmethod
    def _evidence_is_sufficient(sources: list[dict[str, object]], min_sources: int = 2) -> bool:
        """Return whether enough source material exists for a grounded answer."""
        return len(sources) >= min_sources and any(
            str(source.get("snippet") or "").strip() for source in sources
        )

    @staticmethod
    def _format_source(source: dict[str, object]) -> str:
        """Render one normalized source in a readable synthesis context."""
        return "\n".join(
            [
                f"Title: {source.get('title', '')}",
                f"URL: {source.get('url', '')}",
                f"Domain: {source.get('domain', '')}",
                f"Published date: {source.get('published_date') or 'Unknown'}",
                f"Retrieved date: {source.get('retrieved_date') or 'Unknown'}",
                f"Snippet: {source.get('snippet') or 'None'}",
                f"Content: {source.get('content') or 'None'}",
            ]
        )

    def _synthesize(
        self,
        query: str,
        sources: list[dict[str, object]],
        progress_callback: Callable[[dict], None] | None = None,
    ) -> str:
        """Turn collected evidence into a direct, source-grounded answer."""
        if not sources:
            return self.ask(query)

        context = "\n\n".join(self._format_source(source) for source in sources)
        prompt = (
            "=== USER QUERY ===\n"
            f"{query}\n\n"
            "=== COLLECTED EVIDENCE ===\n"
            f"{context}\n\n"
            "=== TASK ===\n"
            "Answer the user's question using the evidence above. "
            "Cite the source material and explain uncertainty or conflicts. "
            "If the evidence is weak or incomplete, say so clearly. "
            "Return the answer itself now; do not describe a future investigation "
            "and do not output planning commentary."
        )
        return self.answer_generator.generate(prompt, progress_callback=progress_callback)

    def research(
        self,
        query: str,
        max_rounds: int = 3,
        min_sources: int = 2,
        num_tasks: int = 3,
        progress_callback: Callable[[dict], None] | None = None,
    ) -> str:
        """Run a bounded research loop until evidence is sufficient or exhausted."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")

        tasks = self.planner.create_plan(query, num_tasks=num_tasks)
        self._report(progress_callback, "planned", total_tasks=len(tasks))
        queue = TaskQueue(tasks)
        collected_sources: list[dict[str, object]] = []
        rounds_without_evidence = 0

        for _ in range(max_rounds):
            task = queue.next_ready()
            if task is None:
                break

            self._report(progress_callback, "task_started", task_id=str(task.id), question=task.question)
            new_sources = self.source_collector.collect(f"{query}\nFocused sub-question: {task.question}")
            collected_sources.extend(new_sources)
            rounds_without_evidence = 0 if new_sources else rounds_without_evidence + 1
            queue.mark_completed(task)

            self._report(
                progress_callback,
                "task_completed",
                task_id=str(task.id),
                question=task.question,
                sources_found=len(new_sources),
                sources=new_sources,
                completed_tasks=sum(item.status == TaskStatus.COMPLETED for item in tasks),
                total_tasks=len(tasks),
            )

            if self._evidence_is_sufficient(collected_sources, min_sources):
                self._report(progress_callback, "finalizing", sources_found=len(collected_sources))
                return self._synthesize(query, collected_sources, progress_callback)

            if rounds_without_evidence >= 2:
                break

        if collected_sources:
            self._report(progress_callback, "finalizing", sources_found=len(collected_sources))
            return self._synthesize(query, collected_sources, progress_callback)

        self._report(progress_callback, "finalizing", sources_found=0)
        return self.ask(query)

    def ask(self, query: str) -> str:
        """Answer a query through the configured answer generator."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")

        if self._requires_web_research(query):
            sources = self.source_collector.collect(query)
            if sources:
                return self._synthesize(query, sources)
            return self.answer_generator.generate(
                "=== USER QUERY ===\n"
                f"{query}\n\n"
                "=== AGENT WEB SEARCH STATUS ===\n"
                "The agent attempted a web search but did not retrieve usable sources.\n\n"
                "=== TASK ===\n"
                "Answer based on your training data and clearly note the lack of dependable web evidence."
            )

        return self.answer_generator.generate(query)

    @staticmethod
    def _requires_web_research(query: str) -> bool:
        """Identify queries that benefit from current or externally grounded evidence."""
        keywords = {
            "what is", "who is", "when did", "where is", "how does",
            "latest", "news", "compare", "explain", "research", "define",
        }
        normalized = query.lower()
        return any(keyword in normalized for keyword in keywords)

    def run_task_queue(
        self,
        tasks: list[ResearchTask],
        worker: Callable[[ResearchTask], object] | None = None,
    ) -> list[tuple[ResearchTask, object]]:
        """Execute tasks in queue order and preserve their lifecycle state."""
        queue = TaskQueue(tasks)
        results: list[tuple[ResearchTask, object]] = []
        handler = worker or (lambda task: self.ask(task.question))

        while queue.has_pending():
            task = queue.next_ready()
            if task is None:
                break
            try:
                results.append((task, handler(task)))
                queue.mark_completed(task)
            except Exception:
                queue.mark_failed(task)
                raise

        return results
