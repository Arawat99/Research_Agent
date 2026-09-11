"""Web source collection for research workflows."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from app.tools.fetch import fetch_source
from app.tools.search import web_search


class WebSourceCollector:
    """Search the web and normalize fetched results into a common shape.

    The collector is the single place where raw search hits and fetched pages
    become the uniform ``dict`` sources the agent consumes.  It also filters
    out material that would be useless as evidence: pages that could not be
    retrieved and come with no search snippet, or duplicate URLs pointing at
    the same page.

    Parameters
    ----------
    search_fn:
        A callable matching the ``web_search`` signature
        ``(query: str, max_results: int) -> list[dict]``.  Defaults to DuckDuckGo;
        pass :func:`app.tools.searxng_search` to use a SearXNG instance.
    max_results:
        Maximum search results to request per query.
    """

    def __init__(
        self,
        *,
        search_fn: Callable[[str, int], list[dict[str, str]]] | None = None,
        max_results: int = 3,
    ):
        self.search_fn = search_fn or web_search
        self.max_results = max_results

    def collect(self, query: str) -> list[dict[str, object]]:
        """Return usable, deduplicated source records for *query*."""
        search_result = self.search_fn(query, self.max_results)
        results = search_result.get("results", []) if isinstance(search_result, dict) else (search_result or [])

        seen_urls: set[str] = set()
        sources: list[dict[str, object]] = []

        for result in results:
            url = str(result.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            snippet = str(result.get("snippet") or "").strip()

            try:
                source = fetch_source(url)
                record = {
                    "title": source.title,
                    "url": str(source.url),
                    "domain": source.domain or urlparse(str(source.url)).hostname or "",
                    "published_date": source.published_date,
                    "retrieved_date": source.retrieved_date.isoformat(),
                    "snippet": (source.snippet or snippet).strip(),
                    "content": source.content or "",
                }
            except (httpx.ConnectError, httpx.TimeoutException):
                record = self._metadata_from_search(result, snippet)
            except Exception:
                # A single broken page should not discard the other search results.
                record = self._metadata_from_search(result, snippet)

            if self._is_usable(record):
                sources.append(record)

        return sources

    @staticmethod
    def _is_usable(source: dict[str, object]) -> bool:
        """Return whether *source* carries enough material to act as evidence.

        A fetched page needs real content; an unfetched page is still kept when
        the search engine provided a substantive snippet, because that snippet
        alone can ground a claim.
        """
        content = str(source.get("content") or "").strip()
        if content:
            return True
        snippet = str(source.get("snippet") or "").strip()
        return len(snippet) >= 80

    @staticmethod
    def _metadata_from_search(result: dict, snippet: str) -> dict[str, object]:
        """Build a source from search metadata when page fetching fails."""
        url = str(result.get("url", ""))
        return {
            "title": result.get("title") or url,
            "url": url,
            "domain": (urlparse(url).hostname or "").removeprefix("www."),
            "published_date": result.get("published_date"),
            "retrieved_date": datetime.now(timezone.utc).isoformat(),
            "snippet": snippet,
            "content": result.get("content", ""),
        }