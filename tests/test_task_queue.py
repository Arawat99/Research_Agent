import unittest
from uuid import uuid4

from app.agent.task_queue import TaskQueue
from app.agent.research_agent import ResearchAgent
from app.models.task import ResearchTask, TaskStatus, PriorityLevel


class FakePlanner:
    def __init__(self, question: str):
        self.question = question

    def create_plan(self, question: str, *, num_tasks: int = 5):
        return [
            ResearchTask(research_id=uuid4(), question=self.question)
            for _ in range(num_tasks)
        ]


class FakeCollector:
    def __init__(self, source_batches):
        self.source_batches = source_batches
        self.calls = 0

    def collect(self, query: str) -> list[dict[str, object]]:
        batch = self.source_batches[min(self.calls, len(self.source_batches) - 1)]
        self.calls += 1
        return batch


class FakeGenerator:
    def __init__(self, answer="answer"):
        self.answer = answer
        self.prompts = []

    def generate(self, prompt, *, progress_callback=None):
        self.prompts.append(prompt)
        return self.answer


class TaskQueueTests(unittest.TestCase):
    def test_queue_prioritizes_pending_tasks_by_priority(self):
        research_id = uuid4()
        queue = TaskQueue([
            ResearchTask(research_id=research_id, question="low", priority=PriorityLevel.LOW),
            ResearchTask(research_id=research_id, question="high", priority=PriorityLevel.HIGH),
            ResearchTask(research_id=research_id, question="medium", priority=PriorityLevel.MEDIUM),
        ])

        next_task = queue.next_ready()
        self.assertEqual(next_task.question, "high")
        self.assertEqual(queue.peek().question, "medium")

    def test_agent_processes_queue_sequentially(self):
        research_id = uuid4()
        agent = ResearchAgent(model="openrouter/free")
        tasks = [
            ResearchTask(research_id=research_id, question="first", priority=PriorityLevel.LOW),
            ResearchTask(research_id=research_id, question="second", priority=PriorityLevel.HIGH),
        ]

        results = agent.run_task_queue(tasks, worker=lambda task: task.question.upper())

        self.assertEqual([item[0].question for item in results], ["second", "first"])
        self.assertEqual([item[1] for item in results], ["SECOND", "FIRST"])
        self.assertTrue(all(task.status == TaskStatus.COMPLETED for task in tasks))

    def test_research_retries_when_evidence_is_insufficient(self):
        strong_evidence = [
            {"title": "Source 1", "url": "https://example.com/1", "domain": "example.com",
             "snippet": "", "content": "Strong evidence about the impact of X on Y with documented results. " * 40},
            {"title": "Source 2", "url": "https://example.org/2", "domain": "example.org",
             "snippet": "", "content": "A second, independent source confirms the same conclusion about the impact of X on Y. " * 30},
        ]
        collector = FakeCollector([[], strong_evidence])
        agent = ResearchAgent(
            planner=FakePlanner("What is the impact of X on Y?"),
            source_collector=collector,
            answer_generator=FakeGenerator("Final answer based on sufficient evidence."),
        )

        response = agent.research("What is the impact of X on Y?", max_rounds=3)

        self.assertEqual(collector.calls, 2)
        self.assertIn("Final answer", response)

    def test_research_stops_when_no_new_sources_are_found(self):
        agent = ResearchAgent(
            planner=FakePlanner("What is the impact of X on Y?"),
            source_collector=FakeCollector([[]]),
            answer_generator=FakeGenerator("Fallback answer because no new sources were found."),
        )
        agent.ask = lambda query: "Fallback answer because no new sources were found."

        response = agent.research("What is the impact of X on Y?", max_rounds=5, num_tasks=3)

        # The loop collects once per round until two rounds pass with no new
        # sources, then falls back to the direct answer path.
        self.assertIn("Fallback answer", response)

    def test_final_prompt_requires_direct_answer(self):
        agent = ResearchAgent(model="openrouter/free")
        captured = {}
        agent.answer_generator.generate = (
            lambda prompt, **kwargs: captured.setdefault("prompt", prompt) or "answer"
        )

        agent._synthesize("Which degree is ranked #1 for 2026?", [{
            "title": "Ranking source",
            "url": "https://example.com/ranking",
            "domain": "example.com",
            "published_date": "2026-01-01",
            "retrieved_date": "2026-09-03T00:00:00+00:00",
            "snippet": "The ranking summary.",
            "content": "The full ranking content.",
        }])

        self.assertIn("Return the answer itself now", captured["prompt"])
        self.assertIn("do not describe a future investigation", captured["prompt"])


if __name__ == "__main__":
    unittest.main()
