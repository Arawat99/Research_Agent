from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, validator


class Source(BaseModel):
    """A web or document source used during research.

    Attributes
    ----------
    id: UUID
        Unique identifier for the source.
    url: HttpUrl
        URL where the source can be accessed.
    title: str
        Human‑readable title of the source.
    domain: Optional[str]
        Domain part of the URL, cached for convenience.
    content: Optional[str]
        Raw content fetched from the source (may be truncated).
    fetched_at: datetime
        Timestamp when the source was retrieved.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the source.")
    url: HttpUrl = Field(..., description="URL where the source can be accessed.")
    title: str = Field(..., description="Human readable title of the source.")
    domain: Optional[str] = Field(default=None, description="Domain portion of the URL, cached for convenience.")
    content: Optional[str] = Field(default=None, description="Fetched raw content, may be truncated.")
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="When the source was retrieved.")

    @validator("title")
    def title_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v
