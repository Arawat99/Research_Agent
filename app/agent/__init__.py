"""Agent package for the research‑agent project.

Exports the primary ``ResearchAgent`` class that implements the simple
"User Query → LLM → Answer" workflow.
"""

from .research_agent import ResearchAgent

__all__ = ["ResearchAgent"]
