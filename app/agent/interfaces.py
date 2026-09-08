"""Interfaces used by the research agent orchestration layer.

Keeping these contracts small lets the agent depend on capabilities rather than
concrete implementations. Components can therefore be replaced in tests or by
future tools without rewriting the orchestration code.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol, TypeAlias

from app.models.task import ResearchTask

Source: TypeAlias = dict[str, object]
ProgressCallback: TypeAlias = Callable[[dict[str, object]], None]


class Planner(Protocol):
    """Create executable research tasks from a user question."""

    def create_plan(self, question: str, *, num_tasks: int = 5) -> list[ResearchTask]:
        ...


class SourceCollector(Protocol):
    """Collect normalized sources for a research question."""

    def collect(self, query: str) -> list[Source]:
        ...


class AnswerGenerator(Protocol):
    """Generate an answer from a prompt."""

    def generate(
        self,
        prompt: str,
        *,
        progress_callback: ProgressCallback | None = None,
    ) -> str:
        ...


class TaskRunner(Protocol):
    """Execute one research task."""

    def run(self, task: ResearchTask) -> object:
        ...


class ResearchTool(Protocol):
    """Generic capability that can be composed into future agent workflows."""

    name: str

    def run(self, query: str) -> Iterable[Source]:
        ...
