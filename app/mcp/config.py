"""Environment-based configuration for the MCP search adapters.

Follows the project convention of reading runtime configuration from
environment variables (see ``app/LLM/ollama.py``) rather than a central
settings object.
"""

from __future__ import annotations

import os


def purili_url() -> str:
    """Return the Puri.li MCP endpoint URL."""
    return os.getenv("PURLI_URL", "https://puri.li/mcp")


def purili_timeout() -> float:
    """Return the per-request timeout in seconds for Puri.li calls."""
    return float(os.getenv("PURLI_SEARCH_TIMEOUT", "30"))


def arxiv_command() -> str:
    """Return the arxiv-mcp-server executable used as the MCP stdio command.

    The default expects ``arxiv-mcp-server`` to be on ``PATH`` (e.g. via
    ``uv tool install arxiv-mcp-server``).  Override with the full path or a
    different launcher such as ``uvx``.
    """
    return os.getenv("ARXIV_COMMAND", "arxiv-mcp-server")


def arxiv_timeout() -> float:
    """Return the per-request timeout in seconds for arxiv stdio calls."""
    return float(os.getenv("ARXIV_SEARCH_TIMEOUT", "60"))