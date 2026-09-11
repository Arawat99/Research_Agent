"""Source retrieval tool.

Provides a function that downloads a web page and creates a :class:`app.models.source.Source`
instance containing the URL, title, domain and a cleaned text version of the page.

Pages are fetched with bounded retries on transient network errors.  The visible
text is preferred to come from the page's ``<main>`` or ``<article>`` regions
when present, which avoids the boilerplate bars that typically surround the
actual content on modern pages.
"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.models.source import Source
from app.tools.retry import with_retries

DEFAULT_TIMEOUT = 15.0
MAX_CONTENT_CHARS = 20000
# Some sites serve a JS-shell page, or thin content, to clients without these.
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0; +https://example.com)"
}


def _extract_visible_text(soup: BeautifulSoup) -> str:
    """Return the visible text from a parsed document, whitespace‑normalised.

    Scripts, styles and other non‑content elements are removed before extracting
    the text.  Consecutive whitespace is collapsed to a single space.
    """
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    return " ".join(soup.get_text(separator=" ", strip=True).split())


def _main_content(soup: BeautifulSoup) -> str:
    """Return the visible text of the most substantive content region.

    Prefers the ``<main>`` or ``<article>`` regions over the whole document
    body, because both selectors normally enclose the article rather than site
    chrome.  When several regions exist the one with the most text is used; the
    full page body is the fallback.
    """
    regions: list[str] = []
    for region in ("main", "article"):
        node = soup.find(region)
        if node is not None:
            regions.append(_extract_visible_text(node))
    if regions:
        return max(regions, key=len)
    return _extract_visible_text(soup)


def _published_date(soup: BeautifulSoup) -> str | None:
    """Extract a publication date from common page metadata, if present."""
    for selector in (
        {"property": "article:published_time"},
        {"property": "og:published_time"},
        {"name": "datePublished"},
        {"name": "pubdate"},
        {"name": "date"},
    ):
        tag = soup.find("meta", attrs=selector)
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def fetch_source(url: str, timeout: float = DEFAULT_TIMEOUT) -> Source:
    """Retrieve *url* and return a populated :class:`Source` model.

    Parameters
    ----------
    url:
        The absolute URL to fetch.  The function validates that the string is
        non‑empty and raises ``ValueError`` otherwise.
    timeout:
        Seconds to wait for each HTTP request attempt.

    Transient network failures are retried up to 3 times with a short backoff.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non‑empty string")

    def fetch_once() -> tuple[httpx.Response, str]:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, follow_redirects=True, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            return response, response.text

    response, html = with_retries(fetch_once)
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag and title_tag.get_text(strip=True) else str(response.url)

    content = _main_content(soup)[:MAX_CONTENT_CHARS] or None

    parsed_url = urlparse(str(response.url))
    domain = (parsed_url.hostname or urlparse(url).hostname or "").removeprefix("www.")

    published_date = _published_date(soup)
    retrieved_date = datetime.now(timezone.utc)
    snippet = content[:600] if content else None

    return Source(
        url=response.url,
        title=title,
        domain=domain,
        published_date=published_date,
        snippet=snippet,
        content=content,
        retrieved_date=retrieved_date,
        fetched_at=retrieved_date,
    )