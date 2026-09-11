"""Deterministic scoring of collected sources as evidence for a research question.

The research agent must not finalize an answer on weak material.  Having *some*
snippets is not enough — a grounded answer needs sources that are relevant to
the question, come from more than one place, and contain enough substance to
support a claim.

This module keeps all of that decision logic in small, pure functions so the
behaviour is testable without running a network call or an LLM.
"""

from __future__ import annotations

from typing import Mapping, Sequence

Source = Mapping[str, object]

# Domains whose content is almost never useful as research evidence.  Matching
# is done on the registered host (e.g. ``reddit.com`` also covers ``www.reddit.com``).
LOW_AUTHORITY_DOMAINS = {
    "reddit.com",
    "quora.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "instagram.com",
    "youtube.com",
    "pinterest.com",
    "medium.com",
    "linkedin.com",
    "wikipedia.org",
}

# A source that contributes to a grounded answer must expose at least this much
# author-authored text.  Anything shorter is treated as a search hit, not
# evidence.
MIN_SUBSTANCE_CHARS = 200

# The two content fields are considered together; a long snippet is acceptable
# when the page body could not be retrieved.
MIN_SNIPPET_CHARS = 80


def _text(source: Source, *fields: str) -> str:
    """Concatenate the given fields of *source*, ignoring missing/empty values."""
    parts = []
    for field in fields:
        value = source.get(field)
        if isinstance(value, str):
            parts.append(value.strip())
    return "\n".join(parts)


def domain_of(source: Source) -> str:
    """Return the source's authority host lowercase, without ``www.``."""
    domain = str(source.get("domain") or "").strip().lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def has_substance(source: Source) -> bool:
    """Return whether *source* contains enough usable text to support a claim.

    A page that was never fetched (no ``content``) still counts when the search
    snippet is long enough to carry detail on its own.
    """
    content = _text(source, "content")
    if len(content) >= MIN_SUBSTANCE_CHARS:
        return True
    snippet = _text(source, "snippet")
    return len(snippet) >= MIN_SNIPPET_CHARS


def _tokenize(text: str) -> set[str]:
    """Split *text* into lowercase, alphanumeric word tokens."""
    words: set[str] = set()
    for token in text.lower().split():
        cleaned = "".join(ch for ch in token if ch.isalnum())
        if cleaned:
            words.add(cleaned)
    return words


def relevance_score(source: Source, question: str) -> float:
    """Return a 0..1 score of how closely *source* overlaps the question topic.

    The score is the fraction of question keywords that also appear in the
    source's title, snippet, or content.  Stop words are excluded so common
    filler like ``what`` or ``the`` does not dominate the overlap.
    """
    stop_words = {
        "what", "who", "when", "where", "why", "how", "which", "is", "are",
        "was", "were", "the", "a", "an", "of", "in", "on", "for", "with",
        "to", "and", "or", "does", "do", "it", "its", "that", "this",
    }
    question_words = _tokenize(question) - stop_words
    if not question_words:
        # Nothing to compare against — assume relevant.
        return 1.0

    source_text = _tokenize(_text(source, "title", "snippet", "content"))
    overlap = len(question_words & source_text)
    return overlap / len(question_words)


def authority_score(source: Source) -> float:
    """Return a 0..1 score reflecting the source's presumptive authority.

    Government and educational domains are treated as more authoritative;
    user-generated and social media content as less so.  Unknown domains get a
    neutral score — the absence of evidence is not evidence of absence.
    """
    domain = domain_of(source)
    if domain in LOW_AUTHORITY_DOMAINS:
        return 0.0
    if domain.endswith((".gov", ".edu")):
        return 1.0
    if domain == "wikipedia.org":
        return 0.3
    return 0.6


def _distinct_domains(sources: Sequence[Source]) -> int:
    """Count sources that come from different registered hosts."""
    return len({domain_of(source) for source in sources if domain_of(source)})


def evidence_is_sufficient(
    sources: Sequence[Source],
    question: str,
    min_sources: int = 2,
    min_relevance: float = 0.25,
) -> bool:
    """Decide whether the collected sources can support a grounded answer.

    All of the following must hold:

    * At least ``min_sources`` sources carry real substance.
    * The sources are meaningfully relevant to the question.
    * The evidence is not monocultural: it comes from more than one domain
      (or, when only a couple of sources exist, they must be highly relevant).
    * At least one source is not from a low-authority, user-generated domain.

    *question* is used for relevance so that unrelated-but-present search hits
    do not satisfy the gate.
    """
    if not sources or min_sources < 1:
        return False

    substantive = [source for source in sources if has_substance(source)]
    if len(substantive) < min_sources:
        return False

    # Relevance: require every qualifying source to overlap the question, and
    # the average overlap to clear a threshold.  A single weak-but-present hit
    # is not enough to drive a confident final answer.
    scores = [relevance_score(source, question) for source in substantive]
    if any(score == 0.0 for score in scores):
        return False
    if sum(scores) / len(scores) < min_relevance:
        return False

    # Diversity: several sources from the same page (or the same site) repeat
    # one underlying fact, so treat them as a single line of evidence.
    distinct_domains = _distinct_domains(substantive)
    if len(substantive) > 2 and distinct_domains < 2:
        return False
    if distinct_domains < 1:
        return False

    # Authority: at least one substantive source must be non-user-generated.
    return any(authority_score(source) > 0.0 for source in substantive)