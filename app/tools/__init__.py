"""Utility tools for the research agent.

This package provides functions for web searching and source retrieval that are
used by higher‑level components such as the research planner.
"""

from .search import web_search  # noqa: F401
from .fetch import fetch_source  # noqa: F401
