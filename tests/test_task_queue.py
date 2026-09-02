import unittest
from uuid import uuid4

from app.agent.task_queue import TaskQueue
from app.agent.research_agent import ResearchAgent
from app.models.task import ResearchTask, TaskStatus, PriorityLevel


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
        agent = ResearchAgent(model="openrouter/free")
        calls = []

        def fake_web_tools(query):
            calls.append(query)
            if len(calls) == 1:
                return []
            return [
                {"title": "Source 1", "url": "https://example.com/1", "snippet": "This is strong evidence about the research topic and the result is documented clearly."},
                {"title": "Source 2", "url": "https://example.com/2", "snippet": "A second source confirms the same conclusion and includes supporting details."},
            ]

        agent._run_web_tools = fake_web_tools
        agent.llm.generate = lambda prompt: "Final answer based on sufficient evidence."

        response = agent.research("What is the impact of X on Y?")

        self.assertEqual(len(calls), 2)
        self.assertIn("Final answer", response)

    def test_research_stops_when_no_new_sources_are_found(self):
        agent = ResearchAgent(model="openrouter/free")
        calls = []

        def fake_web_tools(query):
            calls.append(query)
            return []

        agent._run_web_tools = fake_web_tools
        agent.ask = lambda query: "Fallback answer because no new sources were found."

        response = agent.research("What is the impact of X on Y?", max_rounds=5, num_tasks=3)

        self.assertEqual(len(calls), 2)
        self.assertIn("Fallback answer", response)


if __name__ == "__main__":
    unittest.main()
