"""Source retrieval tool.

Provides a function that downloads a web page and creates a :class:`app.models.source.Source`
instance containing the URL, title, domain and a cleaned text version of the page.
"""

from __future__ import annotations

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
    domain = urlparse(url).netloc

    source = Source(url=url, title=title, domain=domain, content=content)
    return source
