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
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, follow_redirects=True)
        resp.raise_for_status()
        return resp.text


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Perform a web search using DuckDuckGo and return structured results.

    Parameters
    ----------
    query:
        The search query string.
    max_results:
        Upper bound on the number of results to return.
    Returns
    -------
    List[Dict[str, str]]
        Each dictionary has ``title``, ``url`` and ``snippet`` keys.  ``snippet``
        may be empty if the source page does not provide a short description.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non‑empty string")

    try:
        html = _duckduckgo_html(query)
    except Exception:
        # Network problems or unexpected HTML errors – return empty list.
        return []
    soup = BeautifulSoup(html, "lxml")
    results: List[Dict[str, str]] = []

    # DuckDuckGo places each result inside a <div class="result"> container.
    # The clickable title resides in an <a class="result__a"> tag and the
    # human‑readable URL is often encoded as the ``uddg`` query parameter.
    # DuckDuckGo returns each result as an <a class="result__a"> link.  The
    # surrounding `<div class="result">` container is optional for the snippet.
    # We collect up to *max_results* anchors directly.
    for a_tag in soup.select("a.result__a")[:max_results]:
        raw_href = a_tag.get("href", "")
        # The real destination URL is often stored in the "uddg" query parameter.
        parsed_href = urllib.parse.urlparse(raw_href)
        qs = urllib.parse.parse_qs(parsed_href.query)
        url = qs.get("uddg", [raw_href])[0]
        title = a_tag.get_text(strip=True)
        # Attempt to locate a sibling snippet element.
        snippet_tag = a_tag.find_next("a", class_="result__snippet") or a_tag.find_next("div", class_="result__snippet")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        results.append({"title": title, "url": url, "snippet": snippet})

    return results
