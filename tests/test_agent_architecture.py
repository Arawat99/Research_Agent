import unittest
from uuid import uuid4

from app.agent.research_agent import ResearchAgent
from app.models.task import ResearchTask


class FakePlanner:
    def create_plan(self, question: str, *, num_tasks: int = 5):
        return [ResearchTask(research_id=uuid4(), question=question)]


class FakeCollector:
    def __init__(self, sources):
        self.sources = sources
        self.queries = []

    def collect(self, query: str):
        self.queries.append(query)
        return self.sources


class FakeGenerator:
    def __init__(self, answer="answer"):
        self.answer = answer
        self.prompts = []

    def generate(self, prompt, *, progress_callback=None):
        self.prompts.append(prompt)
        return self.answer


class ResearchAgentArchitectureTests(unittest.TestCase):
    def test_dependencies_can_be_injected(self):
        collector = FakeCollector([])
        generator = FakeGenerator("fallback")
        agent = ResearchAgent(
            planner=FakePlanner(),
            source_collector=collector,
            answer_generator=generator,
        )

        result = agent.research("research question", max_rounds=1)

        self.assertEqual(result, "fallback")
        self.assertEqual(len(collector.queries), 1)
        self.assertEqual(generator.prompts, ["research question"])

    def test_synthesis_uses_collector_and_generator_contracts(self):
        collector = FakeCollector([
            {"title": "Source", "url": "https://example.com", "snippet": "Evidence"}
        ])
        generator = FakeGenerator("grounded answer")
        agent = ResearchAgent(
            planner=FakePlanner(),
            source_collector=collector,
            answer_generator=generator,
        )

        result = agent.research("research question", max_rounds=1, min_sources=1)

        self.assertEqual(result, "grounded answer")
        self.assertIn("COLLECTED EVIDENCE", generator.prompts[0])
        self.assertIn("Evidence", generator.prompts[0])

    def test_web_detection_isolated_from_execution(self):
        self.assertTrue(ResearchAgent._requires_web_research("What is Python?"))
        self.assertTrue(ResearchAgent._requires_web_research("latest AI news"))
        self.assertFalse(ResearchAgent._requires_web_research("Write a short poem"))


if __name__ == "__main__":
    unittest.main()
