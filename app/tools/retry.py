"""Bounded retry helper for transient network failures.

The search and fetch tools talk to external services that occasionally time out
or return a temporary server error.  Retrying a bounded number of times with a
small delay makes the research loop resilient without letting a single request
head towards an unbounded number of attempts.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import httpx

# Raised for requests that are safe to retry: network/transport problems and
# temporary server-side status codes (HTTP 429 and 5xx).  Deliberately *not*
# catching other exceptions, so genuine client bugs surface immediately.
TransientError = (httpx.TransportError, httpx.TimeoutException, httpx.ConnectError)


def is_transient_error(exc: Exception) -> bool:
    """Return whether *exc* represents a failure that retrying could fix."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, TransientError)


T = TypeVar("T")


def with_retries(
    call: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
) -> T:
    """Run *call*, retrying up to *attempts* times on transient errors.

    Delays grow linearly (``base_delay``, ``2*base_delay``, ...) so retries do
    not hammer an already-strained endpoint.  The final transient error is
    re-raised so callers can decide how to degrade.
    """
    attempt = 1
    while True:
        try:
            return call()
        except Exception as exc:
            if attempt >= attempts or not is_transient_error(exc):
                raise
            delay = base_delay * attempt
            time.sleep(delay)
            attempt += 1