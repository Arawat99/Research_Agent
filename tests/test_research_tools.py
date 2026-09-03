import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from app.agent.research_agent import ResearchAgent
from app.models.source import Source
from app.tools.search import web_search


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
        self.assertEqual(source.snippet, "Example article Article content.")
        self.assertIsInstance(source.retrieved_date, datetime)
        self.assertEqual(source.retrieved_date, source.fetched_at)

    @patch("app.agent.research_agent.fetch_source")
    @patch("app.agent.research_agent.web_search")
    def test_agent_passes_source_metadata_to_llm(self, web_search_mock, fetch_source_mock):
        web_search_mock.return_value = [{
            "title": "Search title",
            "url": "https://nih.gov/article",
            "snippet": "Search summary",
        }]
        fetch_source_mock.return_value = Source(
            title="Published title",
            url="https://nih.gov/article",
            domain="nih.gov",
            published_date="2026-09-01",
            snippet="Page summary",
            content="Full article content",
        )
        agent = ResearchAgent(model="openrouter/free")
        captured = {}
        agent.llm.generate = lambda prompt: captured.setdefault("prompt", prompt) or "answer"

        agent._finalize_answer("What happened?", agent._run_web_tools("What happened?"))

        self.assertIn("Domain: nih.gov", captured["prompt"])
        self.assertIn("Published date: 2026-09-01", captured["prompt"])
        self.assertIn("Retrieved date:", captured["prompt"])
        self.assertIn("Snippet: Page summary", captured["prompt"])
        self.assertIn("Content: Full article content", captured["prompt"])

    def test_web_search_returns_results(self):
        results = web_search("large language model", max_results=3)
        self.assertGreater(len(results), 0)
        self.assertIn("url", results[0])

    def test_agent_uses_web_tools_for_research_queries(self):
        agent = ResearchAgent()
        results = agent._run_web_tools("What is a large language model?")
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
