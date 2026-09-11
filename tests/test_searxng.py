"""Tests for the SearXNG search provider and collector integration."""

import json
import unittest
from unittest.mock import Mock, patch

from app.tools.searxng import _parse_results, searxng_search
from app.agent.source_collector import WebSourceCollector


class SearXNGSearchTests(unittest.TestCase):
    def test_empty_query_raises_value_error(self):
        with self.assertRaises(ValueError):
            searxng_search("", instance_url="https://searx.example.com")

    def test_empty_instance_url_raises_value_error(self):
        with self.assertRaises(ValueError):
            searxng_search("python", instance_url="")

    def test_whitespace_only_query_raises_value_error(self):
        with self.assertRaises(ValueError):
            searxng_search("   ", instance_url="https://searx.example.com")

    @patch("app.tools.searxng.with_retries")
    def test_successful_search_returns_normalised_results(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Python.org", "url": "https://python.org", "content": "Official site"},
                {"title": "Wikipedia", "url": "https://wikipedia.org/wiki/Python", "content": "Encyclopedia entry"},
            ]
        }
        mock_retry.return_value = mock_response

        results = searxng_search("python", instance_url="https://searx.example.com")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Python.org")
        self.assertEqual(results[0]["url"], "https://python.org")
        self.assertEqual(results[0]["snippet"], "Official site")
        self.assertEqual(results[1]["title"], "Wikipedia")

    @patch("app.tools.searxng.with_retries")
    def test_network_failure_returns_empty_list(self, mock_retry):
        mock_retry.side_effect = Exception("connection refused")

        results = searxng_search("python", instance_url="https://searx.example.com")

        self.assertEqual(results, [])

    @patch("app.tools.searxng.with_retries")
    def test_malformed_json_returns_empty_list(self, mock_retry):
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("err", "", 0)
        mock_retry.return_value = mock_response

        results = searxng_search("python", instance_url="https://searx.example.com")

        self.assertEqual(results, [])

    @patch("app.tools.searxng.with_retries")
    def test_max_results_limits_output(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": f"Result {i}", "url": f"https://example.com/{i}", "content": f"Snippet {i}"}
                for i in range(10)
            ]
        }
        mock_retry.return_value = mock_response

        results = searxng_search("query", instance_url="https://searx.example.com", max_results=3)

        self.assertEqual(len(results), 3)

    @patch("app.tools.searxng.with_retries")
    def test_duplicate_urls_are_deduplicated(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": "First", "url": "https://example.com/a", "content": "A"},
                {"title": "Second", "url": "https://example.com/a", "content": "A dup"},
                {"title": "Third", "url": "https://example.com/b", "content": "B"},
            ]
        }
        mock_retry.return_value = mock_response

        results = searxng_search("query", instance_url="https://searx.example.com")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["url"], "https://example.com/a")
        self.assertEqual(results[1]["url"], "https://example.com/b")

    @patch("app.tools.searxng.with_retries")
    def test_results_without_title_are_skipped(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": "", "url": "https://example.com/no-title", "content": "No title"},
                {"title": "Valid", "url": "https://example.com/valid", "content": "Has title"},
            ]
        }
        mock_retry.return_value = mock_response

        results = searxng_search("query", instance_url="https://searx.example.com")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Valid")

    @patch("app.tools.searxng.with_retries")
    def test_results_without_url_are_skipped(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"title": "No URL", "url": "", "content": "Missing URL"},
                {"title": "Valid", "url": "https://example.com/ok", "content": "Good"},
            ]
        }
        mock_retry.return_value = mock_response

        results = searxng_search("query", instance_url="https://searx.example.com")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "https://example.com/ok")

    @patch("app.tools.searxng.with_retries")
    def test_missing_results_key_returns_empty_list(self, mock_retry):
        mock_response = Mock()
        mock_response.json.return_value = {"query": "python"}
        mock_retry.return_value = mock_response

        results = searxng_search("python", instance_url="https://searx.example.com")

        self.assertEqual(results, [])

    @patch("app.tools.searxng.httpx.Client")
    def test_trailing_slash_in_instance_url_is_handled(self, mock_client_cls):
        """Trailing slash in instance URL should not cause double-slash in path."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_response

        results = searxng_search("test", instance_url="https://searx.example.com/")

        self.assertEqual(results, [])
        # Verify the URL passed to httpx doesn't contain a double slash after host
        call_args = mock_client_cls.return_value.__enter__.return_value.get.call_args
        actual_url = call_args[0][0]
        self.assertNotIn("example.com//", actual_url)


class CollectorSearchFnTests(unittest.TestCase):
    def test_collector_uses_custom_search_fn(self):
        calls = []

        def fake_search(query: str, max_results: int):
            calls.append((query, max_results))
            return [
                {"title": "SearXNG result", "url": "https://example.com/sx", "snippet": "From SearXNG"},
            ]

        collector = WebSourceCollector(search_fn=fake_search, max_results=5)
        results = collector.collect("test query")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "test query")
        self.assertEqual(calls[0][1], 5)

    def test_collector_defaults_to_web_search(self):
        collector = WebSourceCollector()
        from app.tools.search import web_search
        self.assertIs(collector.search_fn, web_search)


if __name__ == "__main__":
    unittest.main()
