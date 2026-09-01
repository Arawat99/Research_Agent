import unittest

from app.agent.research_agent import ResearchAgent
from app.tools.search import web_search


class ResearchToolsTests(unittest.TestCase):
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
