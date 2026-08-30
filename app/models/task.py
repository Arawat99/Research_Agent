from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PriorityLevel(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ResearchTask(BaseModel):
    """A granular task belonging to a Research project.

    Attributes
    ----------
    id: UUID
        Unique identifier for the task.
    research_id: UUID
        Identifier of the parent Research.
    question: str
        Specific question or objective for the task.
    priority: PriorityLevel
        Priority of the task.
    status: TaskStatus
        Current status of the task.
    created_at: datetime
        When the task was created.
    updated_at: Optional[datetime]
        When the task was last updated.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the task.")
    research_id: UUID = Field(..., description="Identifier of the parent Research.")
    question: str = Field(..., description="Specific question or objective for the task.")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Priority of the task.")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the task was created.")
    updated_at: Optional[datetime] = Field(default=None, description="When the task was last updated.")
