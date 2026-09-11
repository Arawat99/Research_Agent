"""SearXNG search provider.

Thin wrapper around the SearXNG JSON API.  SearXNG instances expose a
``/search?format=json`` endpoint that returns results from multiple
engines in one call.  This module calls that API via ``httpx`` (already
in requirements.txt) and normalises the response to the same
``[{"title", "url", "snippet"}]`` shape the rest of the pipeline expects.
"""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List

import httpx

from app.tools.retry import with_retries

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0; +https://example.com)"
}


def _validate(instance_url: str, query: str) -> None:
    """Raise early if required arguments are missing or blank."""
    if not isinstance(instance_url, str) or not instance_url.strip():
        raise ValueError("instance_url must be a non-empty string")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")


def _parse_results(data: Any, max_results: int) -> List[Dict[str, str]]:
    """Extract title/url/snippet dicts from the SearXNG JSON response."""
    results_list = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results_list, list):
        return []

    parsed: List[Dict[str, str]] = []
    for item in results_list[:max_results * 2]:  # fetch extra for dedup headroom
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        title = str(item.get("title") or "").strip()
        if not url or not title:
            continue
        parsed.append({
            "title": title,
            "url": url,
            "snippet": str(item.get("content") or "").strip(),
        })

    # Deduplicate by URL, keeping first occurrence.
    seen: set[str] = set()
    unique: List[Dict[str, str]] = []
    for result in parsed:
        if result["url"] in seen:
            continue
        seen.add(result["url"])
        unique.append(result)

    return unique[:max_results]


def searxng_search(
    query: str,
    instance_url: str,
    max_results: int = 5,
) -> List[Dict[str, str]]:
    """Search a SearXNG instance and return normalised result dicts.

    Each result has the keys ``title``, ``url`` and ``snippet``, matching
    the shape produced by :func:`app.tools.search.web_search` so the rest
    of the pipeline can swap backends without changes.

    Parameters
    ----------
    query:
        The search query.
    instance_url:
        Base URL of the SearXNG instance, e.g. ``https://searx.example.com``.
    max_results:
        Maximum number of results to return (default 5).

    Returns
    -------
    list[dict[str, str]]
        Search results, or an empty list on transient / parse failures.
    """
    _validate(instance_url, query)

    base = instance_url.rstrip("/")
    encoded_query = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "categories": "general",
        "language": "en",
    })
    url = f"{base}/search?{encoded_query}"

    def _fetch() -> httpx.Response:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, follow_redirects=True, headers=DEFAULT_HEADERS)
            resp.raise_for_status()
            return resp

    try:
        response = with_retries(_fetch)
        data = response.json()
    except Exception:
        return []

    return _parse_results(data, max_results)
