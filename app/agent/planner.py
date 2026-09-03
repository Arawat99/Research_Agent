"""Research planner – decomposes a high‑level research question into concrete tasks.

The planner uses the project's LLM abstraction to ask an LLM to generate a JSON
array of sub‑questions.  If the LLM call fails or the output cannot be parsed, a
simple fallback splits the original question on punctuation.
"""

from __future__ import annotations

import json
import re
from typing import List
from uuid import UUID, uuid4

from app.models.task import ResearchTask, PriorityLevel, TaskStatus
from app.LLM import get_llm
from app.prompts.loader import add_system_prompt, load_prompts


class ResearchPlanner:
    """Create a structured plan for a research question.

    The public method :meth:`create_plan` returns a list of :class:`ResearchTask`
    objects that can later be persisted and executed by a manager component.
    """

    def __init__(self, model: str = "openrouter/free", provider: str | None = None):
        # Reuse the same LLM abstraction used by ``ResearchAgent``.
        self.llm = get_llm(model=model, provider=provider)
        self.system_prompt = load_prompts()

    def _plan_prompt(self, question: str, num: int) -> str:
        """Construct a prompt that asks the LLM to output a JSON list of tasks."""
        return (
            f"You are helping to plan a research project. Given the top‑level research "
            f"question below, generate exactly {num} concise sub‑questions or tasks that "
            f"together would allow a researcher to answer the original question. Return "
            f"the tasks as a JSON array of strings and nothing else.\n\n"
            f"Question:\n{question}\n"
        )

    def _parse_llm_output(self, output: str) -> List[str]:
        """Extract a list of task strings from the raw LLM output.

        The LLM may wrap the JSON in markdown fences or add surrounding text.
        This method attempts to locate the JSON, parse it, and fall back to a
        line‑based split if parsing fails.
        """
        cleaned = output.strip()
        # Remove markdown fences if present.
        if cleaned.startswith("```"):
            # Find the closing fence.
            end = cleaned.rfind("```")
            if end != -1:
                cleaned = cleaned[3:end].strip()
        # Try to decode JSON.
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
        except Exception:
            pass
        # Fallback: split on line breaks or list markers.
        lines = [line.strip("- *\t ") for line in cleaned.splitlines()]
        return [l for l in lines if l]

    def create_plan(
        self,
        question: str,
        research_id: UUID | None = None,
        num_tasks: int = 5,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
    ) -> List[ResearchTask]:
        """Generate a list of :class:`ResearchTask` objects for *question*.

        Parameters
        ----------
        question:
            The high‑level research question.
        research_id:
            Identifier of the parent ``Research`` object. If omitted a temporary
            UUID is generated – callers should replace it with the real ID after
            persisting the ``Research`` record.
        num_tasks:
            Desired number of sub‑tasks.
        priority:
            Default priority for all generated tasks.
        """
        if research_id is None:
            research_id = uuid4()
        # Ask the LLM for a JSON list of tasks.
        try:
            raw = self.llm.generate(
                add_system_prompt(self._plan_prompt(question, num_tasks), self.system_prompt)
            )
            task_strings = self._parse_llm_output(raw)
        except Exception:
            task_strings = []

        # If the LLM did not return usable tasks, fall back to a simple heuristic.
        if not task_strings:
            fragments = re.split(r"[\.\n;]", question)
            task_strings = [frag.strip() for frag in fragments if frag.strip()][:num_tasks]

        # Trim to the requested number of tasks.
        task_strings = task_strings[:num_tasks]

        tasks: List[ResearchTask] = []
        for txt in task_strings:
            task = ResearchTask(
                research_id=research_id,
                question=txt,
                priority=priority,
                status=TaskStatus.PENDING,
            )
            tasks.append(task)
        return tasks
