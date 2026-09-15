import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from app.agent.research_agent import ResearchAgent
from app.models.source import Source


class FakeCollector:
    def __init__(self, sources):
        self.sources = sources

    def collect(self, query: str):
        return self.sources


class FakeGenerator:
    def __init__(self, answer="answer"):
        self.answer = answer

    def generate(self, prompt, *, progress_callback=None):
        return self.answer


class ResearchToolsTests(unittest.TestCase):
    @patch("app.tools.fetch.httpx.Client")
    def test_fetch_source_extracts_structured_metadata(self, client_class):
        response = Mock()
        response.text = """
        <html><head>
          <title>Example article</title>
          <meta property="article:published_time" content="2026-09-01T12:00:00Z">
        </head><body><main>Article content.</main></body></html>
        """
        response.url = "https://www.nih.gov/articles/example"
        response.raise_for_status.return_value = None
        client_class.return_value.__enter__.return_value.get.return_value = response

        from app.tools.fetch import fetch_source

        source = fetch_source("https://www.nih.gov/articles/example")

        self.assertEqual(source.title, "Example article")
        self.assertEqual(source.domain, "nih.gov")
        self.assertEqual(source.published_date, "2026-09-01T12:00:00Z")
        self.assertEqual(source.snippet, "Article content.")
        self.assertIsInstance(source.retrieved_date, datetime)
        self.assertEqual(source.retrieved_date, source.fetched_at)

    def test_synthesis_prompt_carries_full_source_metadata(self):
        agent = ResearchAgent(model="openrouter/free")
        captured = {}
        agent.answer_generator.generate = (
            lambda prompt, **kwargs: captured.setdefault("prompt", prompt) or "answer"
        )

        agent._synthesize("What happened?", [{
            "title": "Published title",
            "url": "https://nih.gov/article",
            "domain": "nih.gov",
            "published_date": "2026-09-01",
            "retrieved_date": "2026-09-03T00:00:00+00:00",
            "snippet": "Page summary",
            "content": "Full article content",
        }])

        self.assertIn("Domain: nih.gov", captured["prompt"])
        self.assertIn("Published date: 2026-09-01", captured["prompt"])
        self.assertIn("Retrieved date:", captured["prompt"])
        self.assertIn("Snippet: Page summary", captured["prompt"])
        self.assertIn("Content: Full article content", captured["prompt"])

    @patch("app.tools.search._duckduckgo_html")
    def test_web_search_parses_and_dedupes_results(self, html_mock):
        html_mock.return_value = """
        <html><body>
          <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa">Title A</a>
          <div class="result__snippet">Snippet A</div>
          <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa">Title A dup</a>
          <a class="result__a" href="/nix">No title</a>
        </body></html>
        """
        from app.tools.search import web_search

        results = web_search("large language model", max_results=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "https://example.com/a")
        self.assertIn("url", results[0])

    @patch("app.agent.source_collector.fetch_source")
    @patch("app.agent.source_collector.web_search")
    def test_collector_filters_empty_pages(self, web_search_mock, fetch_source_mock):
        web_search_mock.return_value = [
            {"title": "Full page", "url": "https://example.com/ok", "snippet": "Good snippet"},
            {"title": "Empty page", "url": "https://example.com/empty", "snippet": "ss"},
        ]
        fetch_source_mock.side_effect = [
            Source(
                title="Full page", url="https://example.com/ok", domain="example.com",
                snippet="Good snippet", content="Real content to support a claim",
            ),
            Source(
                title="Empty page", url="https://example.com/empty", domain="example.com",
                snippet="ss", content=None,
            ),
        ]
        from app.agent.source_collector import WebSourceCollector

        sources = WebSourceCollector(max_results=3).collect("test query")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["url"], "https://example.com/ok")

    def test_ask_uses_collector_fallback_when_no_sources(self):
        agent = ResearchAgent(
            source_collector=FakeCollector([]),
            answer_generator=FakeGenerator("no evidence answer"),
        )
        result = agent.ask("What is a large language model?")

        self.assertEqual(result, "no evidence answer")


class CollectorContentTests(unittest.TestCase):
    """Content recovery: inline search content, fallback fetch, and scope."""

    @patch("app.agent.source_collector.fetch_source")
    def test_uses_inline_search_content_without_fetching(self, fetch_source_mock):
        from app.agent.source_collector import WebSourceCollector

        results = [
            {"title": "Paper", "url": "https://arxiv.org/abs/2301.00001",
             "snippet": "abs", "content": "Some abstract about learning."}
        ]
        sources = WebSourceCollector(search_fn=lambda q, n: results).collect("q")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["content"], "Some abstract about learning.")
        self.assertEqual(sources[0]["content_source"], "search_result")
        fetch_source_mock.assert_not_called()

    @patch("app.agent.source_collector.fetch_source")
    def test_content_fn_rescues_pages_the_fetch_cannot_read(self, fetch_source_mock):
        from app.agent.source_collector import WebSourceCollector

        fetch_source_mock.side_effect = RuntimeError("unreachable")
        results = [{"title": "Page", "url": "https://example.com/js", "snippet": "s"}]
        content_fn = lambda url: "Full text recovered via MCP."

        sources = WebSourceCollector(
            search_fn=lambda q, n: results,
            content_fn=content_fn,
        ).collect("q")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["content"], "Full text recovered via MCP.")
        self.assertEqual(sources[0]["content_source"], "fallback")

    @patch("app.agent.source_collector.fetch_source")
    def test_degrades_to_metadata_when_fetch_and_fallback_fail(self, fetch_source_mock):
        from app.agent.source_collector import WebSourceCollector

        fetch_source_mock.side_effect = RuntimeError("unreachable")
        long_snippet = ("A search snippet long enough on its own to ground a claim even when "
                        "the page itself could not be recovered.")
        results = [{"title": "Page", "url": "https://example.com/blocked", "snippet": long_snippet}]

        sources = WebSourceCollector(
            search_fn=lambda q, n: results,
            content_fn=lambda url: None,
        ).collect("q")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["content"], "")
        self.assertNotIn("content_source", sources[0])

    @patch("app.agent.source_collector.fetch_source")
    def test_forwards_scope_to_keyword_capable_backend(self, fetch_source_mock):
        from app.agent.source_collector import WebSourceCollector

        fetch_source_mock.side_effect = RuntimeError("unreachable")
        calls = []

        def scoped_backend(query, max_results, *, domain=None):
            calls.append((query, max_results, domain))
            return [{
                "title": "t",
                "url": f"https://{domain}/x",
                # Long enough on its own to survive the usability filter when the
                # page itself cannot be fetched.
                "snippet": ("A snippet long enough to ground a claim on its own even "
                            "when the page cannot be recovered."),
            }]

        sources = WebSourceCollector(search_fn=scoped_backend).collect(
            "q", scope={"domain": "arxiv.org", "unknown": "dropped"}
        )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["url"], "https://arxiv.org/x")
        self.assertEqual(calls, [("q", 3, "arxiv.org")])

    def test_constructor_scope_merges_with_call_scope(self):
        from app.agent.source_collector import WebSourceCollector

        calls = []

        def scoped_backend(query, max_results, *, domain=None, categories=None):
            calls.append((query, max_results, domain, categories))
            return [{"title": "t", "url": "https://example.com/x", "snippet": "s"}]

        collector = WebSourceCollector(
            search_fn=scoped_backend, search_scope={"domain": "example.com"}
        )
        collector.collect("q", scope={"categories": ["cs.AI"]})

        self.assertEqual(calls, [("q", 3, "example.com", ["cs.AI"])])

    def test_plain_backend_receives_no_scope(self):
        from app.agent.source_collector import WebSourceCollector

        calls = []

        def plain_backend(query, max_results):
            calls.append((query, max_results))
            return [{"title": "t", "url": "https://example.com/x", "snippet": "s"}]

        WebSourceCollector(search_fn=plain_backend).collect("q", scope={"domain": "x"})

        self.assertEqual(calls, [("q", 3)])


if __name__ == "__main__":
    unittest.main()