"""Puri.li MCP search provider.

Puri.li is a hosted MCP server (streamable HTTP, no API key) with its own
independent web index.  This adapter normalises ``web_search`` and
``search_domain`` to the project's ``[{title, url, snippet}]`` shape, and
``get_context`` provides a page-content fallback for URLs already stored in
Puri.li's index.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastmcp.client.transports.http import StreamableHttpTransport

from .client import SearchError, run_tool
from .config import purili_timeout, purili_url


def _dedupe(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate URLs, keeping the first occurrence of each."""
    seen: set[str] = set()
    unique: List[Dict[str, str]] = []
    for result in results:
        url = result["url"]
        if url in seen:
            continue
        seen.add(url)
        unique.append(result)
    return unique


def _normalize(results: Any) -> List[Dict[str, str]]:
    """Map Puri.li result items onto ``{title, url, snippet}``."""
    normalized: List[Dict[str, str]] = []
    for item in results if isinstance(results, list) else []:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        title = str(item.get("title") or "").strip()
        if not url or not title:
            continue
        normalized.append({
            "title": title,
            "url": url,
            "snippet": str(item.get("description") or "").strip(),
        })
    return _dedupe(normalized)


def _search(tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
    """Run a Puri.li search tool and return normalized results.

    Transient or API failures degrade to an empty list so the research loop can
    treat the outcome as "no evidence" and fall back to another backend.
    """
    try:
        payload = run_tool(
            StreamableHttpTransport(purili_url()),
            tool_name,
            arguments,
            timeout=purili_timeout(),
        )
        results = payload.get("results") if isinstance(payload, dict) else None
        return _normalize(results)
    except SearchError:
        return []


def web_search(
    query: str,
    max_results: int = 5,
    *,
    domain: str | None = None,
) -> List[Dict[str, str]]:
    """Search Puri.li's independent web index.

    Parameters
    ----------
    query:
        The search query.
    max_results:
        Maximum number of results to return (Puri.li pages hold 10).
    domain:
        When given, restrict the search to *domain* and its subdomains (the
        ``search_domain`` tool), e.g. ``"arxiv.org"``.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if domain:
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")
        return _search("search_domain", {"query": query, "domain": domain})[:max_results]

    return _search("web_search", {"query": query})[:max_results]


def search_domain(
    query: str,
    domain: str,
    max_results: int = 5,
) -> List[Dict[str, str]]:
    """Search Puri.li restricted to *domain* and its subdomains.

    Thin wrapper around :func:`web_search` for call sites that prefer an
    explicit function per capability.
    """
    return web_search(query, max_results=max_results, domain=domain)


def get_context(url: str) -> str | None:
    """Return stored page content for *url*, or ``None`` when unavailable.

    Used by the source collector as a content fallback for URLs a plain HTTP
    fetch could not read (JS-rendered or bot-blocked pages).  Content is
    returned only when Puri.li actually has a stored copy; ``None`` lets the
    caller continue down its normal fallback chain.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    try:
        payload = run_tool(
            StreamableHttpTransport(purili_url()),
            "get_context",
            {"url": url},
            timeout=purili_timeout(),
        )
    except SearchError:
        return None

    content = payload.get("content") if isinstance(payload, dict) else None
    if isinstance(content, str) and content.strip():
        return content.strip()
    return None