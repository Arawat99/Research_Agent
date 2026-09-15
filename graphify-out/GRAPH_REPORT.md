# Graph Report - research agent  (2026-09-15)

## Corpus Check
- 54 files · ~86,612 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 606 nodes · 1051 edges · 43 communities (39 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2720e6a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ResearchTask
- LLMBase
- test_research_tools.py
- ResearchAgent
- test_agent_architecture.py
- Features
- Research Workflow
- Main weak implementation areas
- main.py
- frontend/research.py
- Usage Guide
- load_prompts
- API Reference
- Overview
- Documentation for the Research Agent
- research
- server/__init__.py
- models/research.py
- frontend/__init__.py
- OpenRouterLLM
- Agent live quality test
- Agent Architecture
- Source
- agent/__init__.py
- searxng_search
- WebSourceCollector
- OllamaLLM
- ResearchPlanner
- LLMProviderSelectionTests
- Design Principles
- README.md
- FallbackLLM
- Installation
- Usage
- Project Vision
- XkiroLLM
- with_retries
- research_agent.py
- fetch_source
- .collect
- Evidence
- cli.py

## God Nodes (most connected - your core abstractions)
1. `ResearchAgent` - 39 edges
2. `ResearchTask` - 34 edges
3. `TaskQueue` - 24 edges
4. `LLMProviderSelectionTests` - 24 edges
5. `get_llm()` - 23 edges
6. `Source` - 19 edges
7. `searxng_search()` - 19 edges
8. `LLMBase` - 18 edges
9. `XkiroLLM` - 18 edges
10. `WebSourceCollector` - 17 edges

## Surprising Connections (you probably didn't know these)
- `LLMProviderSelectionTests` --uses--> `OpenRouterLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/openrouter.py
- `LLMProviderSelectionTests` --uses--> `FallbackLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/router.py
- `LLMProviderSelectionTests` --uses--> `XkiroError`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/xkiro.py
- `LLMProviderSelectionTests` --uses--> `XkiroLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/xkiro.py
- `PlannerFallbackTests` --uses--> `ResearchPlanner`  [INFERRED]
  tests/test_evidence_quality.py → app/agent/planner.py

## Import Cycles
- None detected.

## Communities (43 total, 3 thin omitted)

### Community 0 - "ResearchTask"
Cohesion: 0.14
Nodes (7): Execute tasks in queue order and preserve their lifecycle state., Ordered work queue for research tasks. Tasks are processed in priority order,…, TaskQueue, BaseModel, A granular task belonging to a Research project. Attributes ---------- id: UUID…, ResearchTask, FakePlanner

### Community 1 - "LLMBase"
Cohesion: 0.12
Nodes (12): LLMBase, Any, Base abstraction for LLM providers. This module defines the abstract interface…, Abstract base class for LLM providers. Sub‑classes must implement two primary…, Create a new provider instance. Args: model: The identifier of the model to use…, Generate a completion for *prompt*. Args: prompt: The prompt text to send to…, Perform a chat completion. Args: messages: A list of message dictionaries with…, Top‑level package for LLM abstractions. The public API consists of the… (+4 more)

### Community 2 - "test_research_tools.py"
Cohesion: 0.17
Nodes (4): FakeCollector, FakeGenerator, patch, ResearchToolsTests

### Community 3 - "ResearchAgent"
Cohesion: 0.11
Nodes (11): Run a bounded research loop until evidence is sufficient or exhausted., Answer a query through the configured answer generator., Identify queries that benefit from current or externally grounded evidence., Coordinate the research workflow without owning individual capabilities., Return whether the collected sources can support a grounded answer. The check…, Render one normalized source in a readable synthesis context., Turn collected evidence into a direct, source-grounded answer., ResearchAgent (+3 more)

### Community 4 - "test_agent_architecture.py"
Cohesion: 0.26
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

### Community 12 - "load_prompts"
Cohesion: 0.19
Nodes (8): Generate a response and optionally emit streamed answer deltas., add_system_prompt(), load_prompts(), Load the agent's prompt instructions from the prompts directory., Return all supported prompt files in deterministic filename order., Prefix a task prompt with the configured agent instructions., Path, PromptLoaderTests

### Community 13 - "API Reference"
Cohesion: 0.13
Nodes (14): API Reference, `app.agent.planner.ResearchPlanner`, `app.agent.research_agent.ResearchAgent`, `app.agent.task_queue.TaskQueue`, `ask(query: str) -> str`, `GET /health`, `GET /research/{job_id}`, `GET /research/{job_id}/stream` (+6 more)

### Community 14 - "Overview"
Cohesion: 0.25
Nodes (7): Core components, Current workflow, Intended use, Overview, Provider strategy, Research loop behavior, Source-aware synthesis

### Community 15 - "Documentation for the Research Agent"
Cohesion: 0.40
Nodes (4): API (`docs/api.md`), Documentation for the Research Agent, Overview (`docs/overview.md`), Usage (`docs/usage.md`)

### Community 18 - "models/research.py"
Cohesion: 0.33
Nodes (6): BaseModel, Enum, str, Top‑level research project model. Attributes ---------- id: UUID Unique…, Research, ResearchStatus

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

### Community 24 - "agent/__init__.py"
Cohesion: 0.13
Nodes (15): LLMAnswerGenerator, LLM-backed answer generation for the research agent., Generate answers through the project's provider-agnostic LLM interface., Composable components for the research-agent workflow., AnswerGenerator, Planner, Interfaces used by the research agent orchestration layer. Keeping these…, Create executable research tasks from a user question. (+7 more)

### Community 25 - "searxng_search"
Cohesion: 0.17
Nodes (10): _parse_results(), Any, Raise early if required arguments are missing or blank., Extract title/url/snippet dicts from the SearXNG JSON response., Search a SearXNG instance and return normalised result dicts. Each result has…, searxng_search(), _validate(), patch (+2 more)

### Community 26 - "WebSourceCollector"
Cohesion: 0.14
Nodes (16): Web source collection for research workflows., Search the web and normalize fetched results into a common shape. The collector…, WebSourceCollector, _dedupe(), _duckduckgo_html(), _is_usable(), Web search tool. Provides a simple DuckDuckGo HTML search implementation that…, Perform a web search using DuckDuckGo and return a flat list of result dicts.… (+8 more)

### Community 27 - "OllamaLLM"
Cohesion: 0.16
Nodes (10): OllamaError, OllamaLLM, Any, RuntimeError, Run a chat completion via Ollama's ``/api/chat`` endpoint. ``messages`` should…, Raised when communication with the Ollama server fails., LLM provider that talks to an Ollama server. The default endpoint is…, Internal helper to POST *payload* to *path* and decode JSON. Errors from the… (+2 more)

### Community 28 - "ResearchPlanner"
Cohesion: 0.19
Nodes (9): UUID, Generate a list of :class:`ResearchTask` objects for *question*. Parameters…, Return lowercase alphanumeric word tokens in *text*., Create a structured plan for a research question. The public method…, Construct a prompt that asks the LLM to output a JSON list of tasks., Extract a list of task strings from the raw LLM output. The LLM may wrap the…, Build a deterministic plan when the LLM produced no usable tasks. A question…, ResearchPlanner (+1 more)

### Community 29 - "LLMProviderSelectionTests"
Cohesion: 0.14
Nodes (5): get_llm(), Return a provider selected explicitly or from runtime configuration., Resolve provider configuration from the environment., _resolve_default_provider(), LLMProviderSelectionTests

### Community 30 - "Design Principles"
Cohesion: 0.25
Nodes (8): 1. Evidence over generated knowledge, 2. Modular architecture, 3. Provider independence, 4. Externalized state, 5. Auditable research, 6. Controlled autonomy, 7. Standalone first, composable later, Design Principles

### Community 31 - "README.md"
Cohesion: 0.29
Nodes (6): Architecture, Configuration, Development Roadmap, Future Assistant Hub Integration, Project Structure, Research Agent

### Community 32 - "FallbackLLM"
Cohesion: 0.22
Nodes (10): _build_fallback(), FallbackLLM, _provider_factories(), Any, Pick a model id the xKiro account can serve. Explicit ``vendor/model`` ids are…, Return the concrete provider constructors supported by the application., Try configured providers in order until one returns successfully., Construct available providers without failing during optional setup. (+2 more)

### Community 33 - "Installation"
Cohesion: 0.29
Nodes (7): Clone the repository, Create a virtual environment, Install dependencies, Installation, Linux / WSL, Requirements, Windows

### Community 34 - "Usage"
Cohesion: 0.33
Nodes (6): Basic Research, Check Research Status, Deep Research, Export, Generate Report, Usage

### Community 35 - "Project Vision"
Cohesion: 0.40
Nodes (5): Gradio frontend, HTTP server, Project Vision, Render single service, Status

### Community 36 - "XkiroLLM"
Cohesion: 0.13
Nodes (11): Any, RuntimeError, Yield answer text chunks from xKiro's SSE completion stream., Run a chat completion using the provided *messages* list., Raised when communication with the xKiro API fails., LLM provider that talks to the xKiro API. The provider uses the OpenAI-…, POST *payload* to *path* and decode the JSON response. Errors are wrapped in…, Generate a completion using the chat endpoint with a single user message. The… (+3 more)

### Community 37 - "with_retries"
Cohesion: 0.16
Nodes (10): is_transient_error(), Bounded retry helper for transient network failures. The search and fetch tools…, Return whether *exc* represents a failure that retrying could fix., Run *call*, retrying up to *attempts* times on transient errors. Delays grow…, with_retries(), SearXNG search provider. Thin wrapper around the SearXNG JSON API. SearXNG…, Exception, T (+2 more)

### Community 38 - "research_agent.py"
Cohesion: 0.30
Nodes (8): Research planner – decomposes a high‑level research question into concrete…, Orchestrate planning, source collection, task execution, and synthesis., Data models for the research‑agent application. The module re‑exports the…, PriorityLevel, Enum, str, TaskStatus, int

### Community 39 - "fetch_source"
Cohesion: 0.24
Nodes (11): _extract_visible_text(), fetch_source(), _main_content(), _published_date(), Source retrieval tool. Provides a function that downloads a web page and…, Return the visible text from a parsed document, whitespace‑normalised. Scripts,…, Return the visible text of the most substantive content region. Prefers the…, Extract a publication date from common page metadata, if present. (+3 more)

### Community 40 - ".collect"
Cohesion: 0.33
Nodes (3): Return usable, deduplicated source records for *query*., Return whether *source* carries enough material to act as evidence. A fetched…, Build a source from search metadata when page fetching fails.

### Community 41 - "Evidence"
Cohesion: 0.33
Nodes (4): Evidence, BaseModel, validator, Represents a piece of evidence supporting a claim in a research. Attributes…

### Community 42 - "cli.py"
Cohesion: 0.40
Nodes (4): ask(), Command‑line interface for the ResearchAgent. The CLI uses **Typer** to expose…, Send *query* to the LLM and print the answer. The command simply constructs a…, command

## Knowledge Gaps
- **104 isolated node(s):** `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research`, `📚 Evidence Extraction`, `⭐ Source Evaluation` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 292 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `LLMProviderSelectionTests` to `FallbackLLM`, `LLMBase`, `XkiroLLM`, `research_agent.py`, `load_prompts`, `agent/__init__.py`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `ResearchAgent` connect `ResearchAgent` to `ResearchTask`, `test_research_tools.py`, `test_agent_architecture.py`, `research_agent.py`, `main.py`, `cli.py`, `agent/__init__.py`, `WebSourceCollector`, `ResearchPlanner`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `WebSourceCollector` connect `WebSourceCollector` to `test_research_tools.py`, `ResearchAgent`, `research_agent.py`, `.collect`, `agent/__init__.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ResearchAgent` (e.g. with `ask()` and `LLMAnswerGenerator`) actually correct?**
  _`ResearchAgent` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ResearchTask` (e.g. with `Planner` and `TaskRunner`) actually correct?**
  _`ResearchTask` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `TaskQueue` (e.g. with `ResearchAgent` and `ResearchTask`) actually correct?**
  _`TaskQueue` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `LLMProviderSelectionTests` (e.g. with `OpenRouterLLM` and `FallbackLLM`) actually correct?**
  _`LLMProviderSelectionTests` has 4 INFERRED edges - model-reasoned connections that need verification._