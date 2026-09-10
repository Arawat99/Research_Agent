"""Web source collection for research workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from app.tools.fetch import fetch_source
from app.tools.search import web_search


class WebSourceCollector:
    """Search the web and normalize fetched results into a common shape."""

    def __init__(self, *, max_results: int = 3):
        self.max_results = max_results

    def collect(self, query: str) -> list[dict[str, object]]:
        """Return usable source records without exposing provider-specific details."""
        search_result = web_search(query, max_results=self.max_results)
        results = search_result.get("results", []) if isinstance(search_result, dict) else (search_result or [])

        sources: list[dict[str, object]] = []
        for result in results:
            url = result.get("url")
            if not url:
                continue

            snippet = result.get("snippet") or ""
            try:
                source = fetch_source(url)
                sources.append(
                    {
                        "title": source.title,
                        "url": str(source.url),
                        "domain": source.domain or urlparse(str(source.url)).hostname or "",
                        "published_date": source.published_date,
                        "retrieved_date": source.retrieved_date.isoformat(),
                        "snippet": source.snippet or snippet,
                        "content": source.content or "",
                    }
                )
            except (httpx.ConnectError, httpx.TimeoutException):
                sources.append(self._metadata_from_search(result, snippet))
            except Exception:
                # A single broken page should not discard the other search results.
                sources.append(self._metadata_from_search(result, snippet))

        return sources

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
