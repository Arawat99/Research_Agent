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


def web_search(query: str, max_results: int = 5) -> Dict:
    """Perform a web search using DuckDuckGo and return structured results.

    Parameters
    ----------
    query:
        The search query string.
    max_results:
        Upper bound on the number of results to return.
    Returns
    -------
    Dict
        Contains ``results`` (list of dicts with title/url/snippet), ``error`` (bool),
        and ``error_reason`` (str) if search failed.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non‑empty string")

    try:
        html = _duckduckgo_html(query)
    except httpx.ConnectError as e:
        return {
            "results": [],
            "error": True,
            "error_reason": f"Network connection failed. DuckDuckGo may be temporarily unreachable or blocking automated requests. Details: {str(e)}"
        }
    except httpx.TimeoutException as e:
        return {
            "results": [],
            "error": True,
            "error_reason": f"Search request timed out (10s timeout). The search engine is not responding quickly enough. Details: {str(e)}"
        }
    except Exception as e:
        return {
            "results": [],
            "error": True,
            "error_reason": f"Search failed due to an unexpected error: {type(e).__name__}: {str(e)}"
        }
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
        # DuckDuckGo often gives protocol-relative links such as "//duckduckgo.com/l/?uddg=..."
        # or a direct destination URL. Normalise both forms before extracting the final destination.
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

    if not results:
        return {
            "results": [],
            "error": True,
            "error_reason": f"No search results found for query: '{query}'. The search backend may not have indexed relevant content, or the results are not in a parseable format."
        }
    
    return {
        "results": results,
        "error": False,
        "error_reason": None
    }
