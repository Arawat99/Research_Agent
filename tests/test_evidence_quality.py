"""Quality-focused tests for the evidence gate and planner fallback.

These tests exist because a research agent can pass a wiring test while still
returning weakly-grounded answers.  They assert the *quality* of what the agent
is willing to finalize, not just that a few calls happened.
"""

import unittest

from app.agent.evidence import (
    authority_score,
    evidence_is_sufficient,
    has_substance,
    relevance_score,
)
from app.agent.planner import ResearchPlanner

QUESTION = "How does brain regulation affect memory retention?"


def source(**overrides: object) -> dict[str, object]:
    """Build a realistic source dict with sensible defaults."""
    base = {
        "title": "Regulation study",
        "url": "https://nih.gov/memory",
        "domain": "nih.gov",
        "published_date": "2026-01-01",
        "retrieved_date": "2026-09-03T00:00:00+00:00",
        "snippet": "Brain regulation and memory retention are closely linked.",
        "content": (
            "Brain regulation influences memory retention through multiple "
            "mechanisms. " * 20
        ),
    }
    base.update(overrides)
    return base


class EvidenceQualityTests(unittest.TestCase):
    def test_no_sources_is_never_sufficient(self):
        self.assertFalse(evidence_is_sufficient([], QUESTION, min_sources=2))

    def test_weak_sources_are_rejected(self):
        # User-generated domain, no substantive content, no relevance overlap.
        weak = [
            source(domain="reddit.com", url="https://reddit.com/a", content="", snippet="hi"),
            source(domain="reddit.com", url="https://reddit.com/b", content="", snippet="again"),
        ]
        self.assertFalse(evidence_is_sufficient(weak, QUESTION, min_sources=2))

    def test_same_domain_sources_count_as_one_line_of_evidence(self):
        # Two pages from one site repeat one underlying fact.
        same_domain = [
            source(url="https://nih.gov/a"),
            source(url="https://nih.gov/b"),
            source(url="https://nih.gov/c"),
        ]
        self.assertFalse(evidence_is_sufficient(same_domain, QUESTION, min_sources=2))

    def test_irrelevant_but_substantive_sources_are_rejected(self):
        # Substantive pages exist, but none of them say anything about the
        # question's topic, so they cannot ground an answer about brain regulation.
        irrelevance = [
            source(title="Cooking recipes", url="https://a.com/1", domain="a.com",
                   snippet="", content="Ways to bake bread and knead dough " * 30),
            source(title="Car repairs", url="https://b.com/2", domain="b.com",
                   snippet="", content="Brake maintenance and engine repair steps " * 30),
        ]
        self.assertFalse(evidence_is_sufficient(irrelevance, QUESTION, min_sources=2))

    def test_diverse_and_grounded_sources_are_accepted(self):
        strong = [
            source(url="https://nih.gov/memory", domain="nih.gov"),
            source(url="https://who.int/brain", domain="who.int",
                   title="Memory study", content="Memory and brain regulation data " * 30),
        ]
        self.assertTrue(evidence_is_sufficient(strong, QUESTION, min_sources=2))

    def test_fetch_metadata_only_with_good_snippet_can_qualify(self):
        # A page that failed to fetch is still evidence if the search snippet
        # carries real detail.
        qualified = [
            source(content="", snippet="Brain regulation and memory retention are linked." * 6),
            source(content="Memory retention depends on brain regulation. " * 30),
        ]
        self.assertTrue(evidence_is_sufficient(qualified, QUESTION, min_sources=2))

    def test_has_substance_requires_real_text(self):
        self.assertFalse(has_substance({"title": "x", "content": "", "snippet": ""}))
        self.assertTrue(has_substance({"title": "x", "content": "enough text here " * 40}))

    def test_authority_scoring(self):
        self.assertEqual(authority_score({"domain": "reddit.com"}), 0.0)
        self.assertEqual(authority_score({"domain": "www.nih.gov"}), 1.0)
        self.assertEqual(authority_score({"domain": "ucsd.edu"}), 1.0)

    def test_relevance_overlap_is_meaningful(self):
        relevant = source(
            title="Memory retention regulation findings",
            snippet="Brain regulation drives memory retention.",
            content="Brain regulation and memory retention are linked. " * 30,
        )
        unrelated = source(
            title="Baking bread recipes",
            url="https://cooking.com/bread",
            domain="cooking.com",
            snippet="How to knead dough and bake sourdough.",
            content="Flour, water, salt and yeast produce bread. " * 30,
        )
        self.assertGreater(relevance_score(relevant, QUESTION), relevance_score(unrelated, QUESTION))


class PlannerFallbackTests(unittest.TestCase):
    def setUp(self):
        self.planner = ResearchPlanner.__new__(ResearchPlanner)

    def test_long_question_yields_distinct_facets(self):
        tasks = self.planner._fallback_plan(
            "How does artificial intelligence affect climate modeling accuracy?", 3
        )
        self.assertEqual(len(tasks), 3)
        # Distinct tasks, each one still anchored to the original question.
        self.assertTrue(all("climate modeling" in task.lower() for task in tasks))
        self.assertEqual(len(set(tasks)), len(tasks))

    def test_short_question_stays_single_task(self):
        tasks = self.planner._fallback_plan("What causes inflation?", 3)
        self.assertEqual(tasks, ["What causes inflation?"])

    def test_empty_question_yields_no_tasks(self):
        self.assertEqual(self.planner._fallback_plan("   ", 3), [])


if __name__ == "__main__":
    unittest.main()