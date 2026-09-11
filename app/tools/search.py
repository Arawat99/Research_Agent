"""Web search tool.

Provides a simple DuckDuckGo HTML search implementation that returns a list of
result dictionaries containing ``title``, ``url`` and optionally a short
``snippet``.

The function is deliberately lightweight and does not depend on any external
search‑API keys – it scrapes the public HTML results page.  For production use
you would replace this with a proper API client.  Failures that are transient
(connection problems, HTTP 429/5xx) are retried a bounded number of times;
persistent failures degrade to an empty result list so the caller never has to
handle exceptions from a best‑effort search.
"""

from __future__ import annotations

import urllib.parse
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

from app.tools.retry import with_retries

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0; +https://example.com)"
}


def _duckduckgo_html(query: str) -> str:
    """Fetch DuckDuckGo *HTML* search results for *query*.

    The ``html.duckduckgo.com`` endpoint returns a page that can be parsed
    without executing JavaScript.  A short timeout is used because the
    function is intended for automated agents.
    """
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{encoded}"

    def fetch_once() -> str:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, follow_redirects=True, headers=DEFAULT_HEADERS)
            resp.raise_for_status()
            return resp.text

    return with_retries(fetch_once)


def _resolve_url(raw_href: str) -> str:
    """Decode a DuckDuckGo result href into the actual destination URL."""
    if not raw_href:
        return ""

    if not raw_href.startswith(("http://", "https://")):
        raw_href = f"https:{raw_href}"
    parsed = urllib.parse.urlparse(raw_href)

    # DuckDuckGo wraps real URLs in a ``uddg`` redirect parameter.
    redirect = urllib.parse.parse_qs(parsed.query).get("uddg")
    if redirect:
        return redirect[0]

    if parsed.scheme in ("http", "https") and parsed.netloc:
        return raw_href
    return ""


def _is_usable(url: str, title: str) -> bool:
    """Return whether a parsed search result is worth keeping.

    Drops empty URLs, non‑HTTP schemes, results without a title, and the
    DuckDuckGo result page itself.
    """
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    if not title.strip():
        return False
    if parsed.netloc.lower() in {"html.duckduckgo.com", "duckduckgo.com"}:
        return False
    return True


def _dedupe(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate results, keeping the first occurrence of each URL."""
    seen: set[str] = set()
    unique: List[Dict[str, str]] = []
    for result in results:
        url = result.get("url", "")
        if url in seen:
            continue
        seen.add(url)
        unique.append(result)
    return unique


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Perform a web search using DuckDuckGo and return a flat list of result dicts.

    This function intentionally returns the raw result items so callers can treat
    the output like a normal list of search hits.  Each item contains ``title``,
    ``url`` and a ``snippet``.  Network trouble degrades to an empty list rather
    than raising, keeping the research loop simple.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non‑empty string")

    try:
        html = _duckduckgo_html(query)
    except Exception:
        # A search outage should not crash the research loop; the caller can
        # treat an empty list as "no evidence" and continue.
        return []

    soup = BeautifulSoup(html, "lxml")
    raw_results: List[Dict[str, str]] = []

    for a_tag in soup.select("a.result__a")[: max_results * 2]:
        title = a_tag.get_text(strip=True)
        url = _resolve_url(a_tag.get("href", ""))
        if not _is_usable(url, title):
            continue
        snippet_tag = a_tag.find_next("a", class_="result__snippet") or a_tag.find_next("div", class_="result__snippet")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        raw_results.append({"title": title, "url": url, "snippet": snippet})

    return _dedupe(raw_results)[:max_results]