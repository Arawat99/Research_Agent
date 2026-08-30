from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class Evidence(BaseModel):
    """Represents a piece of evidence supporting a claim in a research.

    Attributes
    ----------
    id: UUID
        Unique identifier for the evidence.
    source_id: UUID
        Identifier of the `Source` this evidence originates from.
    claim: str
        The claim or statement that the evidence is meant to support.
    supporting_text: str
        Exact excerpt or summary from the source that supports the claim.
    confidence: float
        Confidence score (0‑1) that the evidence backs the claim.
    created_at: datetime
        Timestamp of when the evidence record was created.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the evidence.")
    source_id: UUID = Field(..., description="Identifier of the Source this evidence originates from.")
    claim: str = Field(..., description="The claim or statement the evidence is meant to support.")
    supporting_text: str = Field(..., description="Exact excerpt or summary from the source that supports the claim.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0‑1) that the evidence backs the claim.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the evidence record was created.")

    @validator("supporting_text")
    def non_empty_support(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("supporting_text must not be empty")
        return v
