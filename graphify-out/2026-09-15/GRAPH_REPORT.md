# Graph Report - research agent  (2026-09-11)

## Corpus Check
- 53 files · ~85,356 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 574 nodes · 986 edges · 36 communities (32 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 42 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2be8ac0a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ResearchTask
- LLMBase
- WebSourceCollector
- ResearchAgent
- test_agent_architecture.py
- Features
- Research Workflow
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
- OpenRouterLLM
- Agent live quality test
- Agent Architecture
- Source
- research_agent.py
- searxng_search
- TaskQueueTests
- OllamaLLM
- .create_plan
- FallbackLLM
- Design Principles
- README.md
- get_llm
- Installation
- Usage
- Project Vision

## God Nodes (most connected - your core abstractions)
1. `ResearchAgent` - 39 edges
2. `ResearchTask` - 34 edges
3. `TaskQueue` - 24 edges
4. `Source` - 19 edges
5. `searxng_search()` - 19 edges
6. `WebSourceCollector` - 17 edges
7. `Features` - 17 edges
8. `LLMBase` - 16 edges
9. `get_llm()` - 16 edges
10. `evidence_is_sufficient()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `LLMProviderSelectionTests` --uses--> `OpenRouterLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/openrouter.py
- `PlannerFallbackTests` --uses--> `ResearchPlanner`  [INFERRED]
  tests/test_evidence_quality.py → app/agent/planner.py
- `ResearchAgentArchitectureTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_agent_architecture.py → app/agent/research_agent.py
- `ResearchToolsTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_research_tools.py → app/agent/research_agent.py
- `TaskQueueTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_task_queue.py → app/agent/research_agent.py

## Import Cycles
- None detected.

## Communities (36 total, 3 thin omitted)

### Community 0 - "ResearchTask"
Cohesion: 0.14
Nodes (8): Execute one research task., TaskRunner, Execute tasks in queue order and preserve their lifecycle state., Ordered work queue for research tasks. Tasks are processed in priority order,…, TaskQueue, BaseModel, A granular task belonging to a Research project. Attributes ---------- id: UUID…, ResearchTask

### Community 1 - "LLMBase"
Cohesion: 0.13
Nodes (11): LLMBase, Any, Base abstraction for LLM providers. This module defines the abstract interface…, Abstract base class for LLM providers. Sub‑classes must implement two primary…, Create a new provider instance. Args: model: The identifier of the model to use…, Generate a completion for *prompt*. Args: prompt: The prompt text to send to…, Perform a chat completion. Args: messages: A list of message dictionaries with…, Top‑level package for LLM abstractions. The public API consists of the… (+3 more)

### Community 2 - "WebSourceCollector"
Cohesion: 0.10
Nodes (10): Search the web and normalize fetched results into a common shape. The collector…, Return usable, deduplicated source records for *query*., Return whether *source* carries enough material to act as evidence. A fetched…, Build a source from search metadata when page fetching fails., WebSourceCollector, FakeCollector, FakeGenerator, patch (+2 more)

### Community 3 - "ResearchAgent"
Cohesion: 0.14
Nodes (12): ask(), Command‑line interface for the ResearchAgent. The CLI uses **Typer** to expose…, Send *query* to the LLM and print the answer. The command simply constructs a…, Run a bounded research loop until evidence is sufficient or exhausted., Answer a query through the configured answer generator., Identify queries that benefit from current or externally grounded evidence., Coordinate the research workflow without owning individual capabilities., Return whether the collected sources can support a grounded answer. The check… (+4 more)

### Community 4 - "test_agent_architecture.py"
Cohesion: 0.23
Nodes (4): FakeCollector, FakeGenerator, FakePlanner, ResearchAgentArchitectureTests

### Community 5 - "Features"
Cohesion: 0.12
Nodes (17): 🔁 Automatic Provider Failover, 🔎 Autonomous Research Workflow, 💾 Checkpointed Agent State, 📝 Cited Reports, ✅ Claim Verification, 🖥️ CLI Interface, ⚠️ Contradiction Detection, 📚 Evidence Extraction (+9 more)

### Community 6 - "Research Workflow"
Cohesion: 0.18
Nodes (11): 10. Generate Report, 1. Receive Research Question, 2. Analyze Objective, 3. Create Research Plan, 4. Execute Research Tasks, 5. Extract Evidence, 6. Evaluate Evidence, 7. Identify Gaps (+3 more)

### Community 7 - "Main weak implementation areas"
Cohesion: 0.12
Nodes (15): 1. Planning logic is shallow and brittle, 2. Evidence sufficiency is too weak, 3. Search/fetch pipeline is fragile, 4. Provider routing is fragile under real-world failures, 5. Validation does not test real answer quality, Main weak implementation areas, Overall assessment, P1 - Fix evidence quality gate (+7 more)

### Community 8 - "main.py"
Cohesion: 0.10
Nodes (31): get, post, Single-process ASGI application for Render deployment., _async_event_stream(), create_research(), _event_stream(), _get_job(), get_research() (+23 more)

### Community 10 - "frontend/research.py"
Cohesion: 0.19
Nodes (19): Any, HTTP client for the research-agent service., Call the research API and return its JSON response., request_json(), Gradio frontend for the research-agent HTTP service., follow_research(), progress_html(), Any (+11 more)

### Community 11 - "Usage Guide"
Cohesion: 0.13
Nodes (14): Activate the project environment, CLI options, Command line usage, Deploy as one Render service, Direct per-instance override, Guardrails in the research loop, Ollama, OpenRouter (+6 more)

### Community 12 - "answer_generator.py"
Cohesion: 0.21
Nodes (9): LLM-backed answer generation for the research agent., Generate a response and optionally emit streamed answer deltas., add_system_prompt(), load_prompts(), Load the agent's prompt instructions from the prompts directory., Return all supported prompt files in deterministic filename order., Prefix a task prompt with the configured agent instructions., Path (+1 more)

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

### Community 20 - "OpenRouterLLM"
Cohesion: 0.18
Nodes (10): OpenRouterError, OpenRouterLLM, Any, RuntimeError, Yield answer text chunks from OpenRouter's SSE completion stream., Run a chat completion using the provided *messages* list., Raised when communication with the OpenRouter API fails., LLM provider that talks to the OpenRouter API. The provider uses the standard… (+2 more)

### Community 21 - "Agent live quality test"
Cohesion: 0.20
Nodes (9): Agent live quality test, Observed response, Quality assessment, Query tested, Recommended follow-up, Strengths, Test method, Verdict (+1 more)

### Community 22 - "Agent Architecture"
Cohesion: 0.50
Nodes (3): Agent Architecture, Component responsibilities, Why this structure?

### Community 23 - "Source"
Cohesion: 0.08
Nodes (28): authority_score(), _distinct_domains(), domain_of(), evidence_is_sufficient(), has_substance(), Deterministic scoring of collected sources as evidence for a research question.…, Return a 0..1 score reflecting the source's presumptive authority. Government…, Count sources that come from different registered hosts. (+20 more)

### Community 24 - "research_agent.py"
Cohesion: 0.14
Nodes (21): LLMAnswerGenerator, Generate answers through the project's provider-agnostic LLM interface., Composable components for the research-agent workflow., AnswerGenerator, Planner, Interfaces used by the research agent orchestration layer. Keeping these…, Create executable research tasks from a user question., Collect normalized sources for a research question. (+13 more)

### Community 25 - "searxng_search"
Cohesion: 0.05
Nodes (44): Web source collection for research workflows., _extract_visible_text(), fetch_source(), _main_content(), _published_date(), Source retrieval tool. Provides a function that downloads a web page and…, Return the visible text from a parsed document, whitespace‑normalised. Scripts,…, Return the visible text of the most substantive content region. Prefers the… (+36 more)

### Community 26 - "TaskQueueTests"
Cohesion: 0.18
Nodes (4): FakeCollector, FakeGenerator, FakePlanner, TaskQueueTests

### Community 27 - "OllamaLLM"
Cohesion: 0.16
Nodes (10): OllamaError, OllamaLLM, Any, RuntimeError, Run a chat completion via Ollama's ``/api/chat`` endpoint. ``messages`` should…, Raised when communication with the Ollama server fails., LLM provider that talks to an Ollama server. The default endpoint is…, Internal helper to POST *payload* to *path* and decode JSON. Errors from the… (+2 more)

### Community 28 - ".create_plan"
Cohesion: 0.18
Nodes (7): UUID, Generate a list of :class:`ResearchTask` objects for *question*. Parameters…, Return lowercase alphanumeric word tokens in *text*., Construct a prompt that asks the LLM to output a JSON list of tasks., Extract a list of task strings from the raw LLM output. The LLM may wrap the…, Build a deterministic plan when the LLM produced no usable tasks. A question…, _tokenize()

### Community 29 - "FallbackLLM"
Cohesion: 0.21
Nodes (6): _build_fallback(), FallbackLLM, Any, Try configured providers in order until one returns successfully., Construct available providers without failing during optional setup., LLMProviderSelectionTests

### Community 30 - "Design Principles"
Cohesion: 0.25
Nodes (8): 1. Evidence over generated knowledge, 2. Modular architecture, 3. Provider independence, 4. Externalized state, 5. Auditable research, 6. Controlled autonomy, 7. Standalone first, composable later, Design Principles

### Community 31 - "README.md"
Cohesion: 0.29
Nodes (6): Architecture, Configuration, Development Roadmap, Future Assistant Hub Integration, Project Structure, Research Agent

### Community 32 - "get_llm"
Cohesion: 0.17
Nodes (7): get_llm(), _provider_factories(), Return the concrete provider constructors supported by the application., Resolve provider configuration from the environment., Return a provider selected explicitly or from runtime configuration., _resolve_default_provider(), ProviderFactory

### Community 33 - "Installation"
Cohesion: 0.29
Nodes (7): Clone the repository, Create a virtual environment, Install dependencies, Installation, Linux / WSL, Requirements, Windows

### Community 34 - "Usage"
Cohesion: 0.33
Nodes (6): Basic Research, Check Research Status, Deep Research, Export, Generate Report, Usage

### Community 35 - "Project Vision"
Cohesion: 0.40
Nodes (5): Gradio frontend, HTTP server, Project Vision, Render single service, Status

## Knowledge Gaps
- **104 isolated node(s):** `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research`, `📚 Evidence Extraction`, `⭐ Source Evaluation` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ResearchAgent` connect `ResearchAgent` to `ResearchTask`, `WebSourceCollector`, `test_agent_architecture.py`, `main.py`, `research_agent.py`, `TaskQueueTests`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `get_llm()` connect `get_llm` to `research_agent.py`, `LLMBase`, `answer_generator.py`, `FallbackLLM`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `WebSourceCollector` connect `WebSourceCollector` to `research_agent.py`, `searxng_search`, `ResearchAgent`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ResearchAgent` (e.g. with `ask()` and `LLMAnswerGenerator`) actually correct?**
  _`ResearchAgent` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ResearchTask` (e.g. with `Planner` and `TaskRunner`) actually correct?**
  _`ResearchTask` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `TaskQueue` (e.g. with `ResearchAgent` and `ResearchTask`) actually correct?**
  _`TaskQueue` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research` to the rest of the system?**
  _104 weakly-connected nodes found - possible documentation gaps or missing edges._