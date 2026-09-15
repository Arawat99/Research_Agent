"""Tests for the MCP-backed search adapters.

The FastMCP tool calls themselves are stubbed so the suite runs offline and
deterministically; the live behaviour against Puri.li and arxiv-mcp-server is
covered by manual verification.  Unit tests focus on result normalisation,
argument validation, and failure degradation.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.mcp.client import SearchError, extract_payload, run_tool

# --- shared fixtures -------------------------------------------------------


def _result(structured_content=None, text=None, is_error=False):
    """Build the shape of a FastMCP CallToolResult."""
    content = []
    if text is not None:
        content.append(SimpleNamespace(type="text", text=text))
    return SimpleNamespace(
        structured_content=structured_content,
        content=content,
        is_error=is_error,
    )


# --- extract_payload -------------------------------------------------------


class ExtractPayloadTests(unittest.TestCase):
    def test_prefers_structured_content(self):
        result = _result(structured_content={"results": [1]}, text="ignored")
        self.assertEqual(extract_payload(result), {"results": [1]})

    def test_parses_json_text_when_no_structured_content(self):
        # arxiv-mcp-server returns the payload as JSON text only.
        result = _result(structured_content=None, text='{"papers": []}')
        self.assertEqual(extract_payload(result), {"papers": []})

    def test_returns_none_for_unparseable_text(self):
        result = _result(structured_content=None, text="not json")
        self.assertIsNone(extract_payload(result))

    def test_returns_none_for_empty_result(self):
        result = _result(structured_content=None, text="")
        self.assertIsNone(extract_payload(result))


# --- run_tool --------------------------------------------------------------


class RunToolTests(unittest.TestCase):
    @patch("app.mcp.client._call_tool", new_callable=unittest.mock.AsyncMock)
    def test_wraps_transport_errors_as_search_error(self, call):
        call.side_effect = RuntimeError("connection refused")
        with self.assertRaisesRegex(SearchError, "connection refused"):
            run_tool(object(), "web_search", {"query": "x"})

    @patch("app.mcp.client._call_tool", new_callable=unittest.mock.AsyncMock)
    def test_passes_through_search_error(self, call):
        call.side_effect = SearchError("tool down")
        with self.assertRaisesRegex(SearchError, "tool down"):
            run_tool(object(), "web_search", {"query": "x"})


# --- Puri.li web_search ----------------------------------------------------


class PuriLiWebSearchTests(unittest.TestCase):
    def test_rejects_blank_query(self):
        from app.mcp.purili import web_search

        with self.assertRaisesRegex(ValueError, "query"):
            web_search("   ")

    @patch("app.mcp.purili.run_tool")
    def test_normalizes_results(self, run_tool):
        from app.mcp.purili import web_search

        run_tool.return_value = {
            "results": [
                {"title": "First", "url": "https://a.example", "description": "snippet one"},
                {"title": "Second", "url": "https://b.example", "description": "snippet two"},
            ]
        }
        self.assertEqual(
            web_search("test", max_results=5),
            [
                {"title": "First", "url": "https://a.example", "snippet": "snippet one"},
                {"title": "Second", "url": "https://b.example", "snippet": "snippet two"},
            ],
        )

    @patch("app.mcp.purili.run_tool")
    def test_dedupes_and_limits(self, run_tool):
        from app.mcp.purili import web_search

        run_tool.return_value = {
            "results": [
                {"title": "A", "url": "https://a.example", "description": "x"},
                {"title": "B", "url": "https://a.example", "description": "duplicate"},
                {"title": "C", "url": "https://c.example", "description": "y"},
            ]
        }
        self.assertEqual(web_search("test", max_results=2), [
            {"title": "A", "url": "https://a.example", "snippet": "x"},
            {"title": "C", "url": "https://c.example", "snippet": "y"},
        ])

    @patch("app.mcp.purili.run_tool")
    def test_degrades_to_empty_on_search_error(self, run_tool):
        from app.mcp.purili import web_search

        run_tool.side_effect = SearchError("rate limited")
        self.assertEqual(web_search("test"), [])

    @patch("app.mcp.purili.run_tool")
    def test_degrades_to_empty_when_no_results_key(self, run_tool):
        from app.mcp.purili import web_search

        run_tool.return_value = {"unexpected": True}
        self.assertEqual(web_search("test"), [])


# --- Puri.li search_domain -------------------------------------------------


class PuriLiSearchDomainTests(unittest.TestCase):
    def test_rejects_blank_query_or_domain(self):
        from app.mcp.purili import search_domain

        with self.assertRaisesRegex(ValueError, "query"):
            search_domain("", "arxiv.org")
        with self.assertRaisesRegex(ValueError, "domain"):
            search_domain("q", "  ")

    @patch("app.mcp.purili.run_tool")
    def test_forwards_domain_and_normalizes(self, run_tool):
        from app.mcp.purili import search_domain

        run_tool.return_value = {
            "results": [
                {"title": "Paper", "url": "https://arxiv.org/abs/2301.1", "description": "abs"}
            ]
        }
        self.assertEqual(
            search_domain("neural", "arxiv.org", max_results=3),
            [{"title": "Paper", "url": "https://arxiv.org/abs/2301.1", "snippet": "abs"}],
        )
        args = run_tool.call_args
        self.assertEqual(args[0][1], "search_domain")
        self.assertEqual(args[0][2], {"query": "neural", "domain": "arxiv.org"})


# --- Puri.li get_context ---------------------------------------------------


class PuriLiGetContextTests(unittest.TestCase):
    @patch("app.mcp.purili.run_tool")
    def test_returns_stored_content(self, run_tool):
        from app.mcp.purili import get_context

        run_tool.return_value = {
            "url": "https://arxiv.org/abs/2301.00001",
            "content": "The full text of the page.",
            "coverage": "full",
        }
        self.assertEqual(
            get_context("https://arxiv.org/abs/2301.00001"),
            "The full text of the page.",
        )
        args = run_tool.call_args
        self.assertEqual(args[0][1], "get_context")
        self.assertEqual(
            args[0][2],
            {"url": "https://arxiv.org/abs/2301.00001"},
        )

    def test_rejects_blank_url(self):
        from app.mcp.purili import get_context

        with self.assertRaisesRegex(ValueError, "url"):
            get_context("  ")

    @patch("app.mcp.purili.run_tool")
    def test_returns_none_on_search_error(self, run_tool):
        from app.mcp.purili import get_context

        run_tool.side_effect = SearchError("rate limited")
        self.assertIsNone(get_context("https://arxiv.org/abs/2301.00001"))

    @patch("app.mcp.purili.run_tool")
    def test_returns_none_when_content_empty(self, run_tool):
        from app.mcp.purili import get_context

        run_tool.return_value = {"content": "   ", "coverage": "partial"}
        self.assertIsNone(get_context("https://arxiv.org/abs/2301.00001"))


# --- arxiv_search ----------------------------------------------------------


class ArxivSearchTests(unittest.TestCase):
    def test_rejects_blank_query(self):
        from app.mcp.arxiv import arxiv_search

        with self.assertRaisesRegex(ValueError, "query"):
            arxiv_search("  ")

    def test_rejects_invalid_sort_by(self):
        from app.mcp.arxiv import arxiv_search

        with self.assertRaisesRegex(ValueError, "sort_by"):
            arxiv_search("q", sort_by="score")

    @patch("app.mcp.arxiv.run_tool")
    def test_normalizes_papers_and_uses_abs_url(self, run_tool):
        from app.mcp.arxiv import arxiv_search

        run_tool.return_value = {
            "papers": [
                {
                    "id": "2301.00001",
                    "versioned_id": "2301.00001v1",
                    "title": "A Paper",
                    "abstract": "Some abstract about learning.",
                    "published": "2023-01-01T00:00:00Z",
                }
            ],
            "total_results": 1,
            "has_more": False,
        }
        self.assertEqual(arxiv_search("learning", max_results=3), [
            {
                "title": "A Paper",
                "url": "https://arxiv.org/abs/2301.00001",
                "snippet": "Some abstract about learning.",
                # The abstract rides along as content so the collector can use
                # it without an extra fetch to arXiv.
                "content": "Some abstract about learning.",
            }
        ])

    @patch("app.mcp.arxiv.run_tool")
    def test_forwards_categories_and_sort(self, run_tool):
        from app.mcp.arxiv import arxiv_search

        run_tool.return_value = {"papers": []}
        arxiv_search("q", max_results=5, sort_by="date", categories=["cs.LG", "cs.AI"])
        args = run_tool.call_args
        self.assertEqual(args[0][1], "search_papers")
        self.assertEqual(
            args[0][2],
            {"query": "q", "max_results": 5, "sort_by": "date", "categories": ["cs.LG", "cs.AI"]},
        )

    @patch("app.mcp.arxiv.run_tool")
    def test_degrades_to_empty_when_binary_unavailable(self, run_tool):
        from app.mcp.arxiv import arxiv_search

        run_tool.side_effect = SearchError("arxiv-mcp-server not found")
        self.assertEqual(arxiv_search("q"), [])

    @patch("app.mcp.arxiv.run_tool")
    def test_degrades_to_empty_when_no_papers_key(self, run_tool):
        from app.mcp.arxiv import arxiv_search

        run_tool.return_value = {"unexpected": True}
        self.assertEqual(arxiv_search("q"), [])


# --- fallback_search -------------------------------------------------------


class FallbackSearchTests(unittest.TestCase):
    def test_requires_at_least_one_backend(self):
        from app.mcp.compose import fallback_search

        with self.assertRaisesRegex(ValueError, "at least one"):
            fallback_search()

    def test_skips_empty_backends_then_uses_first_with_results(self):
        from app.mcp.compose import fallback_search

        empty = lambda q, n: []
        usable = lambda q, n: [{"title": "t", "url": "https://u.example", "snippet": "s"}]
        search = fallback_search(empty, usable, empty)
        self.assertEqual(search("q"), [{"title": "t", "url": "https://u.example", "snippet": "s"}])

    def test_stops_at_first_successful_backend(self):
        from app.mcp.compose import fallback_search

        calls = []

        def first(q, n):
            calls.append("first")
            return [{"title": "a", "url": "https://a.example", "snippet": "1"}]

        def second(q, n):
            calls.append("second")
            return [{"title": "b", "url": "https://b.example", "snippet": "2"}]

        search = fallback_search(first, second)
        self.assertEqual(len(search("q")), 1)
        self.assertEqual(calls, ["first"])

    def test_returns_empty_when_all_backends_empty(self):
        from app.mcp.compose import fallback_search

        empty = lambda q, n: []
        self.assertEqual(fallback_search(empty, empty)("q"), [])


# --- union_search ----------------------------------------------------------


class UnionSearchTests(unittest.TestCase):
    def test_requires_at_least_one_backend(self):
        from app.mcp.compose import union_search

        with self.assertRaisesRegex(ValueError, "at least one"):
            union_search()

    def test_merges_results_from_all_backends(self):
        from app.mcp.compose import union_search

        web = lambda q, n: [{"title": "a", "url": "https://a.example", "snippet": "1"}]
        papers = lambda q, n: [{"title": "b", "url": "https://b.example", "snippet": "2"}]
        self.assertEqual(
            union_search(web, papers)("q"),
            [
                {"title": "a", "url": "https://a.example", "snippet": "1"},
                {"title": "b", "url": "https://b.example", "snippet": "2"},
            ],
        )

    def test_dedupes_by_url_keeping_first(self):
        from app.mcp.compose import union_search

        first = lambda q, n: [{"title": "a", "url": "https://a.example", "snippet": "1"}]
        dup = lambda q, n: [{"title": "copy", "url": "https://a.example", "snippet": "other"}]
        self.assertEqual(union_search(first, dup)("q"), [
            {"title": "a", "url": "https://a.example", "snippet": "1"},
        ])

    def test_keeps_results_from_working_backend_when_one_fails(self):
        from app.mcp.compose import union_search

        failed = lambda q, n: []
        working = lambda q, n: [{"title": "a", "url": "https://a.example", "snippet": "1"}]
        self.assertEqual(union_search(failed, working)("q"), [
            {"title": "a", "url": "https://a.example", "snippet": "1"},
        ])

    def test_caps_total_at_max_results(self):
        from app.mcp.compose import union_search

        many = lambda q, n: [
            {"title": t, "url": f"https://{t}.example", "snippet": "s"}
            for t in ("a", "b", "c", "d")
        ]
        self.assertEqual(len(union_search(many)("q", max_results=2)), 2)


if __name__ == "__main__":
    unittest.main()