"""HTTP client for the research-agent service."""

from __future__ import annotations

import os
from typing import Any

import httpx


API_BASE_URL = os.getenv(
    "RESEARCH_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


def request_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    """Call the research API and return its JSON response."""
    try:
        response = httpx.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Research service unavailable: {exc}") from exc
