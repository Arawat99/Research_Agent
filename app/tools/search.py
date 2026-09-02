"""Web search tool.

Provides a simple DuckDuckGo HTML search implementation that returns a list of
result dictionaries containing ``title``, ``url`` and optionally a short ``snippet``.

The function is deliberately lightweight and does not depend on any external
search‑API keys – it scrapes the public HTML results page.  For production use
you would replace this with a proper API client.
"""

from __future__ import annotations

import urllib.parse
from typing import List, Dict

import httpx
from bs4 import BeautifulSoup


def _duckduckgo_html(query: str) -> str:
    """Fetch DuckDuckGo *HTML* search results for *query*.

    The ``html.duckduckgo.com`` endpoint returns a page that can be parsed
    without executing JavaScript.  A short timeout is used because the
    function is intended for automated agents.
    """
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0; +https://example.com)"}
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, follow_redirects=True, headers=headers)
        resp.raise_for_status()
        return resp.text


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Perform a web search using DuckDuckGo and return a flat list of result dicts.

    This function intentionally returns the raw result items so callers can treat
    the output like a normal list of search hits. The project tests and the
    agent code expect this behaviour directly.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non‑empty string")

    try:
        html = _duckduckgo_html(query)
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        return []

    soup = BeautifulSoup(html, "lxml")
    results: List[Dict[str, str]] = []

    for a_tag in soup.select("a.result__a")[:max_results]:
        raw_href = a_tag.get("href", "")
        normalized_href = raw_href if raw_href.startswith(("http://", "https://")) else f"https:{raw_href}"
        parsed_href = urllib.parse.urlparse(normalized_href)
        qs = urllib.parse.parse_qs(parsed_href.query)
        if qs.get("uddg"):
            url = qs["uddg"][0]
        elif parsed_href.scheme and parsed_href.netloc:
            url = normalized_href
        else:
            url = raw_href
        title = a_tag.get_text(strip=True)
        snippet_tag = a_tag.find_next("a", class_="result__snippet") or a_tag.find_next("div", class_="result__snippet")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        results.append({"title": title, "url": url, "snippet": snippet})

    return results
