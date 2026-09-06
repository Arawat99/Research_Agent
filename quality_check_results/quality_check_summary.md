# Quality Check Summary

## Overall assessment
The current implementation is close to a functional research agent, but several weak areas reduce the quality and reliability of generated responses.

## Main weak implementation areas

### 1. Planning logic is shallow and brittle
- File: `app/agent/planner.py`
- Problem: The fallback plan creation splits the original question by punctuation and line breaks when the LLM output is unusable.
- Impact: This can generate generic, low-signal sub-questions, which weakens the research process and final answer quality.

### 2. Evidence sufficiency is too weak
- File: `app/agent/research_agent.py`
- Problem: The sufficiency check only looks at the number of sources and whether any snippet is non-empty.
- Impact: The agent may stop early with weak, irrelevant, or redundant sources and produce a confident answer without enough real grounding.

### 3. Search/fetch pipeline is fragile
- Files: `app/tools/search.py`, `app/tools/fetch.py`
- Problem: Search relies on scraping DuckDuckGo HTML, and page fetching depends on content structure heuristics.
- Impact: Many pages will produce noisy, partial, or incomplete source content, which harms answer quality.

### 4. Provider routing is fragile under real-world failures
- File: `app/LLM/router.py`
- Problem: Fallback logic is present, but the provider selection and recovery strategy are still brittle in the face of malformed or unavailable backends.
- Impact: The system may fail open or return poor-quality fallback outputs instead of a higher-confidence answer.

### 5. Validation does not test real answer quality
- Files: `tests/`
- Problem: Current tests mostly check wiring, metadata passing, and prompt formatting, not whether the agent gives a grounded and well-supported final answer.
- Impact: Weak implementations can pass the suite while still producing poor quality responses.

## Priority tasks to address

### P1 - Fix evidence quality gate
- Improve `ResearchAgent._evidence_is_sufficient()` to evaluate source relevance, authority, diversity, and completeness.
- Require stronger criteria before finalizing an answer.

### P1 - Strengthen planner output quality
- Replace the punctuation-based fallback with a more meaningful task-generation heuristic.
- Ensure tasks are specific, distinct, and relevant to the original question.

### P1 - Harden retrieval pipeline
- Add retries, better error handling, and relevance filtering for search and fetch functions.
- Reduce dependence on brittle HTML assumptions.

### P2 - Add quality-focused tests
- Add tests that verify the agent rejects weak evidence and prefers grounded answers.
- Cover failure cases and degraded-answer conditions.

### P2 - Improve provider robustness
- Make the fallback behavior more consistent and resilient to empty/malformed provider responses.

## Recommended next step
Start with the evidence-quality gate and the planner fallback, because those are the most direct drivers of low-quality agent responses.
