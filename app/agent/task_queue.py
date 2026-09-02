from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from app.models.task import ResearchTask, TaskStatus


class TaskQueue:
    """Ordered work queue for research tasks.

    Tasks are processed in priority order, with a deterministic queue instead of
    executing every task opportunistically or in insertion order.
    """

    def __init__(self, tasks: Iterable[ResearchTask] | None = None):
        self._tasks: list[ResearchTask] = []
        if tasks:
            for task in tasks:
                self.enqueue(task)

    @staticmethod
    def _priority_key(task: ResearchTask):
        # Highest priority wins first. For equal-priority tasks, older items are
        # drained first to preserve a stable, predictable queue order.
        return (task.priority.value, -task.created_at.timestamp())

    def enqueue(self, task: ResearchTask) -> ResearchTask:
        if not isinstance(task, ResearchTask):
            raise TypeError("TaskQueue items must be ResearchTask instances")
        self._tasks.append(task)
        self._tasks.sort(key=self._priority_key, reverse=True)
        return task

    def peek(self) -> ResearchTask | None:
        for task in self._tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def next_ready(self) -> ResearchTask | None:
        task = self.peek()
        if task is None:
            return None
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow()
        return task

    def mark_completed(self, task: ResearchTask) -> ResearchTask:
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        return task

    def mark_failed(self, task: ResearchTask) -> ResearchTask:
        task.status = TaskStatus.FAILED
        task.updated_at = datetime.utcnow()
        return task

    def has_pending(self) -> bool:
        return any(task.status == TaskStatus.PENDING for task in self._tasks)

    def __iter__(self):
        return iter(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def as_list(self) -> list[ResearchTask]:
        return list(self._tasks)
