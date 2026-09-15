"""arxiv-mcp-server search provider.

Runs the local ``arxiv-mcp-server`` over stdio (no API key).  Only the
``search_papers`` tool is consumed; the server enforces arXiv's ~3-second rate
limit itself.  Results are mapped to the project's ``[{title, url, snippet}]``
shape where ``url`` is the paper's arXiv abstract page (the server returns the
PDF link directly, which is less useful for evidence collection).

Install the server once with::

    uv tool install arxiv-mcp-server
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from fastmcp.client.transports.stdio import StdioTransport

from .client import SearchError, run_tool
from .config import arxiv_command, arxiv_timeout


def _abs_url(paper_id: str) -> str:
    """Return the canonical abstract URL for an arXiv paper id."""
    return f"https://arxiv.org/abs/{paper_id}"


def _normalize(papers: Any) -> List[Dict[str, str]]:
    """Map arxiv-mcp-server paper dicts onto ``{title, url, snippet}``.

    The abstract is attached as ``content`` so the source collector can use it
    without an extra HTTP fetch to arXiv (which rate-limits this network).
    """
    normalized: List[Dict[str, str]] = []
    for paper in papers if isinstance(papers, list) else []:
        if not isinstance(paper, dict):
            continue
        paper_id = str(paper.get("id") or "").strip()
        title = str(paper.get("title") or "").strip()
        if not paper_id or not title:
            continue
        abstract = str(paper.get("abstract") or "").strip()
        normalized.append({
            "title": title,
            "url": _abs_url(paper_id),
            "snippet": abstract,
            "content": abstract,
        })
    return normalized


def arxiv_search(
    query: str,
    max_results: int = 5,
    sort_by: str = "relevance",
    categories: Optional[Sequence[str]] = None,
) -> List[Dict[str, str]]:
    """Search arXiv via the local arxiv-mcp-server.

    Parameters
    ----------
    query:
        The arXiv query string (prefer quoted phrases and ``ti:``/``abs:``
        field prefixes for precision).
    max_results:
        Maximum papers to return (server caps at 50).
    sort_by:
        ``"relevance"`` (default) or ``"date"`` for newest-first.
    categories:
        Optional arXiv category filters, e.g. ``["cs.LG", "cs.AI"]``.

    Returns an empty list on transport or server failure (the arxiv binary may
    not be installed), matching the behaviour of the other search backends.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if sort_by not in ("relevance", "date"):
        raise ValueError("sort_by must be 'relevance' or 'date'")

    arguments: Dict[str, Any] = {
        "query": query,
        "max_results": max_results,
        "sort_by": sort_by,
    }
    if categories is not None:
        arguments["categories"] = list(categories)

    try:
        payload = run_tool(
            StdioTransport(command=arxiv_command(), args=[]),
            "search_papers",
            arguments,
            timeout=arxiv_timeout(),
        )
        papers = payload.get("papers") if isinstance(payload, dict) else None
        return _normalize(papers)[:max_results]
    except SearchError:
        return []