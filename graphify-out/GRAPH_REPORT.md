# Graph Report - research agent  (2026-09-03)

## Corpus Check
- 40 files · ~80,218 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 345 nodes · 555 edges · 21 communities (17 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5ebddd46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- research_agent.py
- OpenRouterLLM
- Source
- ResearchAgent
- OllamaLLM
- Research Workflow
- Features
- Installation
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
- Evidence

## God Nodes (most connected - your core abstractions)
1. `ResearchAgent` - 32 edges
2. `TaskQueue` - 24 edges
3. `ResearchTask` - 24 edges
4. `Features` - 17 edges
5. `OpenRouterLLM` - 14 edges
6. `LLMBase` - 13 edges
7. `get_llm()` - 13 edges
8. `ResearchPlanner` - 13 edges
9. `ResearchJob` - 13 edges
10. `TaskStatus` - 12 edges

## Surprising Connections (you probably didn't know these)
- `ResearchToolsTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_research_tools.py → app/agent/research_agent.py
- `TaskQueueTests` --uses--> `ResearchAgent`  [INFERRED]
  tests/test_task_queue.py → app/agent/research_agent.py
- `LLMProviderSelectionTests` --uses--> `OpenRouterLLM`  [INFERRED]
  tests/test_llm_provider_selection.py → app/LLM/openrouter.py
- `_run_job()` --calls--> `ResearchAgent`  [EXTRACTED]
  server/main.py → app/agent/research_agent.py
- `TaskQueueTests` --uses--> `TaskQueue`  [INFERRED]
  tests/test_task_queue.py → app/agent/task_queue.py

## Import Cycles
- None detected.

## Communities (21 total, 3 thin omitted)

### Community 0 - "research_agent.py"
Cohesion: 0.09
Nodes (21): Agent package for the research‑agent project. Exports the primary…, UUID, Research planner – decomposes a high‑level research question into concrete…, Create a structured plan for a research question. The public method…, Construct a prompt that asks the LLM to output a JSON list of tasks., Extract a list of task strings from the raw LLM output. The LLM may wrap the…, Generate a list of :class:`ResearchTask` objects for *question*. Parameters…, ResearchPlanner (+13 more)

### Community 1 - "OpenRouterLLM"
Cohesion: 0.06
Nodes (29): LLMBase, Any, Base abstraction for LLM providers. This module defines the abstract interface…, Abstract base class for LLM providers. Sub‑classes must implement two primary…, Create a new provider instance. Args: model: The identifier of the model to use…, Generate a completion for *prompt*. Args: prompt: The prompt text to send to…, Perform a chat completion. Args: messages: A list of message dictionaries with…, Top‑level package for LLM abstractions. The public API consists of the… (+21 more)

### Community 2 - "Source"
Cohesion: 0.12
Nodes (17): BaseModel, validator, A web or document source used during research. Attributes ---------- id: UUID…, Source, _extract_visible_text(), fetch_source(), Source retrieval tool. Provides a function that downloads a web page and…, Return the visible text from *html*. Scripts, styles and other non‑content… (+9 more)

### Community 3 - "ResearchAgent"
Cohesion: 0.14
Nodes (13): ask(), Command‑line interface for the ResearchAgent. The CLI uses **Typer** to expose…, Send *query* to the LLM and print the answer. The command simply constructs a…, Return True only when there is enough material to answer the question reliably., Generate a completion with a safe fallback when the provider is empty or…, Ask the LLM to answer once the evidence threshold has been reached., Perform iterative research with a task queue until enough evidence is found., Send *query* to the LLM and return its answer. The underlying LLM implements a… (+5 more)

### Community 4 - "OllamaLLM"
Cohesion: 0.16
Nodes (10): OllamaError, OllamaLLM, Any, RuntimeError, Run a chat completion via Ollama's ``/api/chat`` endpoint. ``messages`` should…, Raised when communication with the Ollama server fails., LLM provider that talks to an Ollama server. The default endpoint is…, Internal helper to POST *payload* to *path* and decode JSON. Errors from the… (+2 more)

### Community 5 - "Research Workflow"
Cohesion: 0.18
Nodes (11): 10. Generate Report, 1. Receive Research Question, 2. Analyze Objective, 3. Create Research Plan, 4. Execute Research Tasks, 5. Extract Evidence, 6. Evaluate Evidence, 7. Identify Gaps (+3 more)

### Community 6 - "Features"
Cohesion: 0.05
Nodes (42): 1. Evidence over generated knowledge, 2. Modular architecture, 3. Provider independence, 4. Externalized state, 5. Auditable research, 6. Controlled autonomy, 7. Standalone first, composable later, Architecture (+34 more)

### Community 7 - "Installation"
Cohesion: 0.29
Nodes (7): Clone the repository, Create a virtual environment, Install dependencies, Installation, Linux / WSL, Requirements, Windows

### Community 8 - "main.py"
Cohesion: 0.18
Nodes (19): get, post, _async_event_stream(), create_research(), _event_stream(), _get_job(), get_research(), health() (+11 more)

### Community 10 - "frontend/research.py"
Cohesion: 0.22
Nodes (14): Any, HTTP client for the research-agent service., Call the research API and return its JSON response., request_json(), Gradio frontend for the research-agent HTTP service., follow_research(), progress_html(), Any (+6 more)

### Community 11 - "Usage Guide"
Cohesion: 0.13
Nodes (14): Activate the project environment, CLI options, Command line usage, Deploy as one Render service, Direct per-instance override, Guardrails in the research loop, Ollama, OpenRouter (+6 more)

### Community 12 - "load_prompts"
Cohesion: 0.26
Nodes (7): add_system_prompt(), load_prompts(), Load the agent's prompt instructions from the prompts directory., Return all supported prompt files in deterministic filename order., Prefix a task prompt with the configured agent instructions., Path, PromptLoaderTests

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

### Community 20 - "Evidence"
Cohesion: 0.33
Nodes (4): Evidence, BaseModel, validator, Represents a piece of evidence supporting a claim in a research. Attributes…

## Knowledge Gaps
- **83 isolated node(s):** `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research`, `📚 Evidence Extraction`, `⭐ Source Evaluation` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 186 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ResearchAgent` connect `ResearchAgent` to `research_agent.py`, `OpenRouterLLM`, `Source`, `main.py`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `get_llm()` connect `OpenRouterLLM` to `research_agent.py`, `load_prompts`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `ResearchTask` connect `research_agent.py` to `ResearchAgent`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ResearchAgent` (e.g. with `ask()` and `ResearchPlanner`) actually correct?**
  _`ResearchAgent` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `TaskQueue` (e.g. with `ResearchAgent` and `ResearchTask`) actually correct?**
  _`TaskQueue` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ResearchTask` (e.g. with `ResearchPlanner` and `ResearchAgent`) actually correct?**
  _`ResearchTask` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `🔎 Autonomous Research Workflow`, `🧠 Research Planning`, `🌐 Multi-Source Research` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._