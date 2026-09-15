"""Web source collection for research workflows."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from app.tools.fetch import fetch_source
from app.tools.search import web_search

#: Signature params that belong to every search backend; never scope keys.
_BASE_PARAMS = {"self", "query", "max_results", "args", "kwargs"}


class WebSourceCollector:
    """Search the web and normalize fetched results into a common shape.

    The collector is the single place where raw search hits and fetched pages
    become the uniform ``dict`` sources the agent consumes.  It also filters
    out material that would be useless as evidence: pages that could not be
    retrieved and come with no search snippet, or duplicate URLs pointing at
    the same page.

    Content is gathered by preference order so a readable page never gets
    discarded for lack of a fetch:

    1. content bundled with the search result (e.g. an arXiv abstract),
    2. a direct page fetch,
    3. an optional ``content_fn`` fallback for pages a plain HTTP fetch cannot
       read (JS-rendered or bot-blocked), e.g. Puri.li ``get_context``,
    4. search metadata alone.

    Parameters
    ----------
    search_fn:
        A callable matching the ``web_search`` signature
        ``(query: str, max_results: int) -> list[dict]``.  Defaults to DuckDuckGo;
        pass :func:`app.tools.searxng_search` to use a SearXNG instance.
    content_fn:
        Optional callable ``(url: str) -> str | None`` returning page content
        for a URL, consulted when a direct fetch fails.  Puri.li's
        ``get_context`` is a natural fit.
    max_results:
        Maximum search results to request per query.
    search_scope:
        Extra keyword arguments forwarded to a scope-aware ``search_fn`` — one
        that declares parameters beyond ``query``/``max_results``, e.g.
        ``{"domain": "arxiv.org"}`` or ``{"categories": ["cs.AI"]}``.  Keys a
        backend does not understand are ignored; a plain backend receives no
        extra arguments.
    """

    def __init__(
        self,
        *,
        search_fn: Callable[..., list[dict[str, str]]] | None = None,
        content_fn: Callable[[str], str | None] | None = None,
        max_results: int = 3,
        search_scope: dict[str, object] | None = None,
    ):
        self.search_fn = search_fn or web_search
        self.content_fn = content_fn
        self.max_results = max_results
        self.search_scope = dict(search_scope or {})

    def collect(
        self,
        query: str,
        *,
        scope: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        """Return usable, deduplicated source records for *query*."""
        merged_scope = {**self.search_scope, **(scope or {})}
        search_result = self._search(query, merged_scope)
        results = (
            search_result.get("results", [])
            if isinstance(search_result, dict)
            else (search_result or [])
        )

        seen_urls: set[str] = set()
        sources: list[dict[str, object]] = []

        for result in results:
            url = str(result.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            snippet = str(result.get("snippet") or "").strip()
            record = self._build_record(result, url, snippet)
            if self._is_usable(record):
                sources.append(record)

        return sources

    def _search(self, query: str, scope: dict[str, object]) -> object:
        """Run the search backend, forwarding *scope* to backends that accept it."""
        if not scope:
            return self.search_fn(query, self.max_results)
        accepted = self._scope_keys(self.search_fn)
        if accepted is None:
            # ``**kwargs`` backend: forward the whole scope.
            forward = dict(scope)
        else:
            forward = {key: value for key, value in scope.items() if key in accepted}
        if forward:
            return self.search_fn(query, self.max_results, **forward)
        return self.search_fn(query, self.max_results)

    @staticmethod
    def _scope_keys(backend: Callable) -> set[str] | None:
        """Extra keyword arguments *backend* can take, beyond query/max_results.

        Returns ``None`` when the backend absorbs any scope via ``**kwargs``.
        """
        try:
            signature = inspect.signature(backend)
        except (TypeError, ValueError):
            return set()
        params = signature.parameters
        if any(param.kind is inspect.Parameter.VAR_KEYWORD for param in params.values()):
            return None
        return {
            name
            for name, param in params.items()
            if name not in _BASE_PARAMS
            and param.kind
            in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            and param.default is not inspect.Parameter.empty
        }

    def _build_record(self, result: dict, url: str, snippet: str) -> dict[str, object]:
        """Build the richest usable record for a single search hit."""
        inline = str(result.get("content") or "").strip()
        if inline:
            record = self._metadata_from_search(result, snippet, content=inline)
            record["content_source"] = "search_result"
            return record

        try:
            source = fetch_source(url)
        except Exception:
            # A single broken/unreachable page should not discard the other
            # search results; give the content fallback a chance, then degrade.
            return self._fallback_record(result, url, snippet)

        return {
            "title": source.title,
            "url": str(source.url),
            "domain": source.domain or urlparse(str(source.url)).hostname or "",
            "published_date": source.published_date,
            "retrieved_date": source.retrieved_date.isoformat(),
            "snippet": (source.snippet or snippet).strip(),
            "content": source.content or "",
            "content_source": "http",
        }

    def _fallback_record(self, result: dict, url: str, snippet: str) -> dict[str, object]:
        """Record via the content fallback, or search metadata when unavailable."""
        if self.content_fn is not None:
            try:
                content = str(self.content_fn(url) or "").strip()
            except Exception:
                content = ""
            if content:
                record = self._metadata_from_search(result, snippet, content=content)
                record["content_source"] = "fallback"
                return record
        return self._metadata_from_search(result, snippet)

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
    def _metadata_from_search(
        result: dict,
        snippet: str,
        content: str = "",
    ) -> dict[str, object]:
        """Build a source from search metadata when page fetching fails."""
        url = str(result.get("url", ""))
        body = content or str(result.get("content", "")).strip()
        return {
            "title": result.get("title") or url,
            "url": url,
            "domain": (urlparse(url).hostname or "").removeprefix("www."),
            "published_date": result.get("published_date"),
            "retrieved_date": datetime.now(timezone.utc).isoformat(),
            "snippet": snippet,
            "content": body,
        }