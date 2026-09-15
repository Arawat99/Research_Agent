"""MCP-backed search providers.

Each adapter talks to an MCP search server (Puri.li, arxiv-mcp-server) and
normalises results to the project's ``[{title, url, snippet}]`` shape, so the
functions can be used directly as the ``search_backend`` of
:class:`~app.agent.research_agent.ResearchAgent`::

    from app.mcp import arxiv_search, fallback_search, web_search

    agent = ResearchAgent(
        model="openrouter/free",
        search_backend=fallback_search(web_search, arxiv_search),
    )
"""

from .arxiv import arxiv_search
from .client import SearchError
from .compose import fallback_search, union_search
from .purili import get_context, search_domain, web_search

__all__ = [
    "SearchError",
    "arxiv_search",
    "fallback_search",
    "get_context",
    "search_domain",
    "union_search",
    "web_search",
]