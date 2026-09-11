import unittest
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

from server.main import (
    ResearchJob,
    ResearchRequest,
    _event_stream,
    _probe_searxng,
    _run_job,
    app,
)


class SearXNGStatusTests(unittest.TestCase):
    def test_unconfigured_instance_is_reported_offline(self):
        with patch("server.main._searxng_base_url", return_value=""):
            status = _probe_searxng()
        self.assertEqual(status["configured"], False)
        self.assertEqual(status["online"], False)
        self.assertEqual(status["json_enabled"], False)

    @patch("server.main.httpx.Client")
    def test_online_with_json_api_available(self, client_class):
        html_response = Mock()
        html_response.raise_for_status.return_value = None
        json_response = Mock(status_code=200)
        client = client_class.return_value.__enter__.return_value
        client.get.side_effect = [html_response, json_response]

        with patch("server.main._searxng_base_url", return_value="https://searx.example.com"):
            status = _probe_searxng()

        self.assertEqual(status, {"configured": True, "online": True, "json_enabled": True})

    @patch("server.main.httpx.Client")
    def test_online_but_json_api_disabled(self, client_class):
        html_response = Mock()
        html_response.raise_for_status.return_value = None
        json_response = Mock(status_code=403)
        client = client_class.return_value.__enter__.return_value
        client.get.side_effect = [html_response, json_response]

        with patch("server.main._searxng_base_url", return_value="https://searx.example.com"):
            status = _probe_searxng()

        self.assertEqual(status["online"], True)
        self.assertEqual(status["json_enabled"], False)

    @patch("server.main.httpx.Client")
    def test_offline_when_html_probe_fails(self, client_class):
        client = client_class.return_value.__enter__.return_value
        client.get.side_effect = httpx.ConnectError("no connection")

        with patch("server.main._searxng_base_url", return_value="https://searx.example.com"):
            status = _probe_searxng()

        self.assertEqual(status["online"], False)
        self.assertEqual(status["json_enabled"], False)

    def test_status_endpoint_returns_probe(self):
        with patch("server.main._probe_searxng", return_value={
            "configured": True, "online": True, "json_enabled": True,
        }):
            response = TestClient(app).get("/search/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["online"], True)

    @patch("server.main.wake_searxng")
    def test_wake_endpoint_returns_immediately(self, wake):
        response = TestClient(app).post("/search/wake")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"waking": True})
        wake.assert_called_once()


class ServerTests(unittest.TestCase):
    @patch("server.main.ResearchAgent")
    def test_background_job_publishes_progress_and_answer(self, agent_class):
        agent = agent_class.return_value

        def fake_research(query, **kwargs):
            kwargs["progress_callback"]({"event": "planned", "total_tasks": 1})
            kwargs["progress_callback"]({"event": "task_started", "task_id": "task-1"})
            kwargs["progress_callback"]({
                "event": "task_completed",
                "sources_found": 1,
                "sources": [{"title": "Example", "url": "https://example.com"}],
            })
            return "answer"

        agent.research.side_effect = fake_research
        job = ResearchJob(ResearchRequest(query="Explain this"))

        _run_job(job)

        self.assertEqual(job.status, "completed")
        self.assertEqual(job.answer, "answer")
        self.assertEqual(
            [event["event"] for event in job.events],
            ["started", "planned", "task_started", "task_completed", "completed"],
        )
        self.assertEqual(job.events[3]["sources"][0]["url"], "https://example.com")

    def test_event_stream_replays_events_until_completion(self):
        job = ResearchJob(ResearchRequest(query="Explain this"))
        job.status = "completed"
        job.publish("completed", answer="answer")

        stream = "".join(_event_stream(job))

        self.assertIn("event: completed", stream)
        self.assertIn('"answer": "answer"', stream)


if __name__ == "__main__":
    unittest.main()