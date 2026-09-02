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


if __name__ == "__main__":
    unittest.main()
