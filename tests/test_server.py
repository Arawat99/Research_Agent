import unittest
from unittest.mock import patch

from server.main import ResearchJob, ResearchRequest, _event_stream, _run_job


class ServerTests(unittest.TestCase):
    @patch("server.main.ResearchAgent")
    def test_background_job_publishes_progress_and_answer(self, agent_class):
        agent = agent_class.return_value

        def fake_research(query, **kwargs):
            kwargs["progress_callback"]({"event": "planned", "total_tasks": 1})
            kwargs["progress_callback"]({"event": "task_started", "task_id": "task-1"})
            return "answer"

        agent.research.side_effect = fake_research
        job = ResearchJob(ResearchRequest(query="Explain this"))

        _run_job(job)

        self.assertEqual(job.status, "completed")
        self.assertEqual(job.answer, "answer")
        self.assertEqual(
            [event["event"] for event in job.events],
            ["started", "planned", "task_started", "completed"],
        )

    def test_event_stream_replays_events_until_completion(self):
        job = ResearchJob(ResearchRequest(query="Explain this"))
        job.status = "completed"
        job.publish("completed", answer="answer")

        stream = "".join(_event_stream(job))

        self.assertIn("event: completed", stream)
        self.assertIn('"answer": "answer"', stream)


if __name__ == "__main__":
    unittest.main()