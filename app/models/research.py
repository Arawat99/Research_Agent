from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ResearchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Research(BaseModel):
    """Top‑level research project model.

    Attributes
    ----------
    id: UUID
        Unique identifier for the research project.
    question: str
        The research question or problem statement.
    status: ResearchStatus
        Current status of the research.
    created_at: datetime
        When the research record was created.
    updated_at: Optional[datetime]
        When the research record was last updated.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the research project.")
    question: str = Field(..., description="Research question or problem statement.")
    status: ResearchStatus = Field(default=ResearchStatus.PENDING, description="Current status of the research.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the research was created.")
    updated_at: Optional[datetime] = Field(default=None, description="When the research was last updated.")
    # Potentially a list of task IDs could be added later as a relationship field.
