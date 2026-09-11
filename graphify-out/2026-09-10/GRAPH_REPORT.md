# Graph Report - research agent  (2026-09-10)

## Corpus Check
- 47 files · ~81,115 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 432 nodes · 699 edges · 23 communities (19 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2be8ac0a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ResearchAgent
- LLMBase
- Source
- cli.py
- .research
- Features
- README.md
- Main weak implementation areas
- main.py
- frontend/research.py
- Usage Guide
- answer_generator.py
- API Reference
- Overview
- Documentation for the Research Agent
- research
- server/__init__.py
- models/__init__.py
- frontend/__init__.py
- OpenRouterError
- Agent live quality test
- Agent Architecture

## God Nodes (most connected - your core abstractions)
1. `ResearchAgent` - 39 edges
2. `ResearchTask` - 32 edges
3. `TaskQueue` - 24 edges
4. `Features` - 17 edges
5. `LLMBase` - 16 edges
6. `get_llm()` - 16 edges
7. `OpenRouterLLM` - 15 edges
8. `ResearchPlanner` - 13 edges
9. `ResearchJob` - 13 edges
10. `OllamaLLM` - 12 edges

## Surprising Connections (you probably didn't know these)
- `ResearchAgentArchitectureTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_agent_architecture.py → app/agent/research_agent.py
- `ResearchToolsTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_research_tools.py → app/agent/research_agent.py
- `FakePlanner` --uses--> `ResearchTask`  [INFERRED]
  tests/test_agent_architecture.py → app/models/task.py
- `LLMProviderSelectionTests` --uses--> `OpenRouterLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/openrouter.py
- `_run_job()` --calls--> `ResearchAgent`  [EXTRACTED]
  server/main.py → app/agent/research_agent.py

## Import Cycles
- None detected.

## Communities (23 total, 3 thin omitted)

### Community 0 - "ResearchAgent"
Cohesion: 0.06
Nodes (36): Composable components for the research-agent workflow., AnswerGenerator, Planner, Interfaces used by the research agent orchestration layer. Keeping these…, Create executable research tasks from a user question., Collect normalized sources for a research question., Generate an answer from a prompt., Execute one research task. (+28 more)

### Community 1 - "LLMBase"
Cohesion: 0.05
Nodes (36): LLMBase, Any, Base abstraction for LLM providers. This module defines the abstract interface…, Abstract base class for LLM providers. Sub‑classes must implement two primary…, Create a new provider instance. Args: model: The identifier of the model to use…, Generate a completion for *prompt*. Args: prompt: The prompt text to send to…, Perform a chat completion. Args: messages: A list of message dictionaries with…, Top‑level package for LLM abstractions. The public API consists of the… (+28 more)

### Community 2 - "Source"
Cohesion: 0.09
Nodes (22): Web source collection for research workflows., Search the web and normalize fetched results into a common shape., Return usable source records without exposing provider-specific details., Build a source from search metadata when page fetching fails., WebSourceCollector, BaseModel, validator, A web or document source used during research. Attributes ---------- id: UUID… (+14 more)

### Community 3 - "cli.py"
Cohesion: 0.40
Nodes (4): ask(), Command‑line interface for the ResearchAgent. The CLI uses **Typer** to expose…, Send *query* to the LLM and print the answer. The command simply constructs a…, command

### Community 4 - ".research"
Cohesion: 0.09
Nodes (10): Answer a query through the configured answer generator., Identify queries that benefit from current or externally grounded evidence., Return whether enough source material exists for a grounded answer., Render one normalized source in a readable synthesis context., Turn collected evidence into a direct, source-grounded answer., Run a bounded research loop until evidence is sufficient or exhausted., FakeCollector, FakeGenerator (+2 more)

### Community 5 - "Features"
Cohesion: 0.12
Nodes (17): 🔁 Automatic Provider Failover, 🔎 Autonomous Research Workflow, 💾 Checkpointed Agent State, 📝 Cited Reports, ✅ Claim Verification, 🖥️ CLI Interface, ⚠️ Contradiction Detection, 📚 Evidence Extraction (+9 more)

### Community 6 - "README.md"
Cohesion: 0.05
Nodes (43): 10. Generate Report, 1. Evidence over generated knowledge, 1. Receive Research Question, 2. Analyze Objective, 2. Modular architecture, 3. Create Research Plan, 3. Provider independence, 4. Execute Research Tasks (+35 more)

### Community 7 - "Main weak implementation areas"
Cohesion: 0.12
Nodes (15): 1. Planning logic is shallow and brittle, 2. Evidence sufficiency is too weak, 3. Search/fetch pipeline is fragile, 4. Provider routing is fragile under real-world failures, 5. Validation does not test real answer quality, Main weak implementation areas, Overall assessment, P1 - Fix evidence quality gate (+7 more)

### Community 8 - "main.py"
Cohesion: 0.18
Nodes (19): get, post, _async_event_stream(), create_research(), _event_stream(), _get_job(), get_research(), health() (+11 more)

### Community 10 - "frontend/research.py"
Cohesion: 0.22
Nodes (14): Any, HTTP client for the research-agent service., Call the research API and return its JSON response., request_json(), Gradio frontend for the research-agent HTTP service., follow_research(), progress_html(), Any (+6 more)

### Community 11 - "Usage Guide"
Cohesion: 0.13
Nodes (14): Activate the project environment, CLI options, Command line usage, Deploy as one Render service, Direct per-instance override, Guardrails in the research loop, Ollama, OpenRouter (+6 more)

### Community 12 - "answer_generator.py"
Cohesion: 0.16
Nodes (11): LLMAnswerGenerator, LLM-backed answer generation for the research agent., Generate answers through the project's provider-agnostic LLM interface., Generate a response and optionally emit streamed answer deltas., add_system_prompt(), load_prompts(), Load the agent's prompt instructions from the prompts directory., Return all supported prompt files in deterministic filename order. (+3 more)

### Community 13 - "API Reference"
Cohesion: 0.13
Nodes (14): API Reference, `app.agent.planner.ResearchPlanner`, `app.agent.research_agent.ResearchAgent`, `app.agent.task_queue.TaskQueue`, `ask(query: str) -> str`, `GET /health`, `GET /research/{job_id}`, `GET /research/{job_id}/stream` (+6 more)

### Community 14 - "Overview"
Cohesion: 0.25
Nodes (7): Core components, Current workflow, Intended use, Overview, Provider strategy, Research loop behavior, Source-aware synthesis

### Community 15 - "Documentation for the Research Agent"
Cohesion: 0.40
Nodes (4): API (`docs/api.md`), Documentation for the Research Agent, Overview (`docs/overview.md`), Usage (`docs/usage.md`)

### Community 18 - "models/__init__.py"
Cohesion: 0.17
Nodes (11): Evidence, BaseModel, validator, Represents a piece of evidence supporting a claim in a research. Attributes…, Data models for the research‑agent application. The module re‑exports the…, BaseModel, Enum, str (+3 more)

### Community 20 - "OpenRouterError"
Cohesion: 0.21
Nodes (8): OpenRouterError, Any, RuntimeError, Yield answer text chunks from OpenRouter's SSE completion stream., Run a chat completion using the provided *messages* list., Raised when communication with the OpenRouter API fails., POST *payload* to *path* and decode the JSON response. Errors are wrapped in…, Generate a completion using the chat endpoint with a single user message. The…

### Community 21 - "Agent live quality test"
Cohesion: 0.20
Nodes (9): Agent live quality test, Observed response, Quality assessment, Query tested, Recommended follow-up, Strengths, Test method, Verdict (+1 more)

### Community 22 - "Agent Architecture"
Cohesion: 0.50
Nodes (3): Agent Architecture, Component responsibilities, Why this structure?

## Knowledge Gaps
- **104 isolated node(s):** `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research`, `📚 Evidence Extraction`, `⭐ Source Evaluation` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 232 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ResearchAgent` connect `ResearchAgent` to `Source`, `cli.py`, `.research`, `main.py`, `answer_generator.py`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `get_llm()` connect `LLMBase` to `ResearchAgent`, `answer_generator.py`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `ResearchTask` connect `ResearchAgent` to `models/__init__.py`, `.research`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ResearchAgent` (e.g. with `ask()` and `LLMAnswerGenerator`) actually correct?**
  _`ResearchAgent` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ResearchTask` (e.g. with `Planner` and `TaskRunner`) actually correct?**
  _`ResearchTask` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `TaskQueue` (e.g. with `ResearchAgent` and `ResearchTask`) actually correct?**
  _`TaskQueue` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LLMBase` (e.g. with `_build_fallback()` and `get_llm()`) actually correct?**
  _`LLMBase` has 2 INFERRED edges - model-reasoned connections that need verification._