"""Compose multiple search backends into one best-effort search.

Two composition strategies are provided:

* :func:`fallback_search` mirrors the LLM fallback pattern in
  ``app/LLM/router.py`` — the first backend that yields at least one usable
  result wins.  Backends that degrade to an empty list (transient failure,
  provider unavailable) are skipped.
* :func:`union_search` merges results from every backend, which broadens
  coverage (e.g. general web plus academic) at the cost of requiring each
  backend to actually run.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Dict, List

SearchBackend = Callable[[str, int], List[Dict[str, str]]]


def fallback_search(*backends: SearchBackend) -> SearchBackend:
    """Return a search that tries each *backend* in order until one succeeds."""
    if not backends:
        raise ValueError("fallback_search requires at least one backend")

    def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        merged: List[Dict[str, str]] = []
        seen: set[str] = set()
        for backend in backends:
            for result in backend(query, max_results) or []:
                url = result.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    merged.append(result)
            if merged:
                break
        return merged[:max_results]

    return search


def union_search(*backends: SearchBackend) -> SearchBackend:
    """Return a search that merges results from every *backend*.

    Results are deduplicated by URL and capped at ``max_results``.  Each backend
    still reports failure with an empty list, so a slow or down provider simply
    contributes nothing rather than aborting the search.
    """
    if not backends:
        raise ValueError("union_search requires at least one backend")

    def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        merged: List[Dict[str, str]] = []
        seen: set[str] = set()
        for backend in backends:
            for result in backend(query, max_results) or []:
                url = result.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    merged.append(result)
        return merged[:max_results]

    return search