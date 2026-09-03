"""Source retrieval tool.

Provides a function that downloads a web page and creates a :class:`app.models.source.Source`
instance containing the URL, title, domain and a cleaned text version of the page.
"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.models.source import Source


def _extract_visible_text(html: str) -> str:
    """Return the visible text from *html*.

    Scripts, styles and other non‑content elements are removed before extracting
    and normalising whitespace.  The result is truncated to a reasonable size to
    keep the stored ``content`` field manageable.
    """
    soup = BeautifulSoup(html, "lxml")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Collapse consecutive whitespace characters.
    return " ".join(text.split())


def fetch_source(url: str, timeout: float = 10.0) -> Source:
    """Retrieve *url* and return a populated :class:`Source` model.

    Parameters
    ----------
    url:
        The absolute URL to fetch.  The function validates that the string is
        non‑empty and raises ``ValueError`` otherwise.
    timeout:
        Seconds to wait for the HTTP request.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non‑empty string")

    with httpx.Client(timeout=timeout) as client:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag and title_tag.get_text(strip=True) else url
    content = _extract_visible_text(html)[:20000]  # truncate to keep payload reasonable
    parsed_url = urlparse(str(response.url))
    domain = (parsed_url.hostname or urlparse(url).hostname or "").removeprefix("www.")

    published_date = None
    for selector in (
        {"property": "article:published_time"},
        {"property": "og:published_time"},
        {"name": "datePublished"},
        {"name": "pubdate"},
        {"name": "date"},
    ):
        tag = soup.find("meta", attrs=selector)
        if tag and tag.get("content"):
            published_date = tag["content"].strip()
            break

    retrieved_date = datetime.now(timezone.utc)
    snippet = content[:600] if content else None

    source = Source(
        url=response.url,
        title=title,
        domain=domain,
        published_date=published_date,
        snippet=snippet,
        content=content,
        retrieved_date=retrieved_date,
        fetched_at=retrieved_date,
    )
    return source
