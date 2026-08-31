# Research Agent

An **autonomous, evidence-based AI research agent** designed to investigate complex questions, gather information from multiple sources, evaluate evidence, verify claims, and produce structured research reports with citations.

The project is designed as a **standalone research system first**, while maintaining a modular architecture that allows it to later operate as a **sub-agent or MCP service for a larger agentic AI system such as Assistant Hub**.

Unlike a simple question-answering chatbot, the Research Agent follows a multi-step research workflow:

```text
Research Question
       ↓
Research Planning
       ↓
Task Decomposition
       ↓
Search & Source Collection
       ↓
Source Analysis
       ↓
Evidence Extraction
       ↓
Source Evaluation
       ↓
Claim Verification
       ↓
Gap & Contradiction Detection
       ↓
Research Iteration
       ↓
Evidence-Based Synthesis
       ↓
Cited Research Report
```

---

## Features

### 🔎 Autonomous Research Workflow

The agent can decompose a research question into smaller research tasks, execute those tasks, collect evidence, and iteratively investigate areas where additional information is required.

Instead of:

```text
User Query → LLM → Answer
```

the intended workflow is:

```text
User Query
    ↓
Research Plan
    ↓
Research Tasks
    ↓
Search
    ↓
Sources
    ↓
Evidence
    ↓
Verification
    ↓
Synthesis
    ↓
Report
```

### 🧠 Research Planning

The agent analyzes the user's objective and creates a structured research plan.

For example:

```text
Question:
Should I use FastMCP for my Assistant Hub?

Research Tasks:
├── What is FastMCP?
├── What capabilities does it provide?
├── How does it work?
├── What are its advantages?
├── What are its limitations?
├── What alternatives exist?
└── Is it appropriate for Assistant Hub?
```

Research tasks can be prioritized and tracked independently.

### 🌐 Multi-Source Research

The agent is designed to retrieve information from multiple types of sources, including:

* Official documentation
* Websites
* Technical articles
* GitHub repositories
* Academic sources
* PDFs
* User-provided documents
* Other supported information sources

The architecture separates **search**, **source retrieval**, and **evidence analysis** so additional research tools can be added without redesigning the agent.

### 📚 Evidence Extraction

Rather than relying exclusively on raw webpage content, the agent extracts structured evidence from sources.

Conceptually:

```text
Source
  ↓
Relevant Information
  ↓
Evidence
  ↓
Claim
```

Evidence can be associated with its original source, location, and confidence.

This provides an auditable connection between the final report and the information used to produce it.

### ⭐ Source Evaluation

Sources can be evaluated using factors such as:

* Authority
* Relevance
* Recency
* Primary-source status
* Corroboration

The system is designed to distinguish stronger evidence, such as official documentation or academic publications, from weaker supporting material.

Source quality is treated as a factor in confidence rather than as an absolute measure of truth.

### ✅ Claim Verification

Important claims can be checked against the collected evidence before appearing in the final report.

Conceptually:

```text
Claim
  ↓
Retrieve Supporting Evidence
  ↓
Does the evidence support the claim?
  ├── Yes → Verified
  ├── Partial → Revise / qualify
  └── No → Remove or investigate further
```

This helps reduce unsupported statements and hallucinated conclusions.

### ⚠️ Contradiction Detection

When sources disagree, the agent can identify potential conflicts instead of blindly combining the information.

For example:

```text
Source A:
Feature X is supported.

Source B:
Feature X is experimental.

Source C:
Feature X is unavailable in version Y.
```

The agent can investigate whether the difference is caused by:

* Version differences
* Different implementations
* Outdated information
* Different definitions
* Actual disagreement between sources

### 🔄 Iterative Research

The agent is designed to determine whether additional research is necessary.

```text
Research
   ↓
Evaluate Coverage
   ↓
Are Important Questions Answered?
   ├── No → Generate Additional Queries
   │          ↓
   │       Research Again
   │
   └── Yes
          ↓
       Verify
          ↓
       Synthesize
```

Research limits such as maximum iterations, sources, and execution time can be configured to prevent uncontrolled execution.

### 📝 Cited Reports

The agent produces structured reports containing:

* Research question
* Executive summary
* Methodology
* Findings
* Comparative analysis
* Conflicting evidence
* Limitations
* Conclusions
* Confidence
* Sources and citations

Reports can initially be generated as Markdown, with additional formats added later.

### 💾 Persistent Research Knowledge

The architecture supports persistent storage of:

```text
Research
├── Research Tasks
├── Sources
├── Evidence
├── Claims
├── Verification Results
└── Reports
```

A future vector retrieval layer can allow previous research and evidence to be reused in subsequent investigations.

### 🔌 Provider-Agnostic LLM Architecture

The Research Agent does not directly depend on a single LLM provider.

The intended architecture is:

```text
Research Agent
      ↓
LLM Interface
      ↓
Provider Gateway
 ┌────┼─────┬─────────┐
 ↓    ↓     ↓         ↓
Claude Ollama Gemini OpenRouter
```

Providers can be added through adapters implementing the common LLM interface.

This allows the agent to support cloud and local models without changing the research workflow.

### 🔁 Automatic Provider Failover

The provider architecture is designed to support automatic recovery from conditions such as:

* Context exhaustion
* Rate limits
* Temporary provider failures
* Timeouts
* Quota exhaustion
* Model unavailability

The intended architecture is:

```text
Primary Provider
      ↓
Failure / Context Limit
      ↓
Context Manager
      ↓
Checkpoint / Compact State
      ↓
Provider Router
      ↓
Fallback Provider
      ↓
Continue Research
```

Agent state is kept separate from the provider conversation so research can continue even when the underlying model changes.

### 💾 Checkpointed Agent State

Long-running research tasks can maintain external state such as:

```text
.agent/
├── state.json
├── checkpoint.md
├── decisions.md
└── tasks.json
```

This allows an interrupted or provider-switched research task to resume from its last known state instead of starting from the beginning.

### 🖥️ CLI Interface

The project is designed to provide a terminal-first interface.

Example:

```bash
research "What are the best open-source AI agent frameworks?"
```

Deep research:

```bash
research "Compare LangGraph, CrewAI, and AutoGen" --depth deep
```

Check a running research task:

```bash
research status <research-id>
```

Generate a report:

```bash
research report <research-id>
```

Export a report:

```bash
research export <research-id> --format markdown
```

### 📦 Library / API Usage

The agent can also be used programmatically.

Example:

```python
from app.agent import ResearchAgent

agent = ResearchAgent()

result = await agent.research(
    "Compare LangGraph and CrewAI for building AI agents."
)

print(result.report)
```

The exact API may evolve during development as the research workflow becomes more sophisticated.

### 🔌 MCP Integration

The completed system is intended to expose research capabilities through MCP.

Potential tools include:

```text
research_start
research_status
research_cancel
research_search
research_sources
research_evidence
research_verify
research_report
research_export
```

This allows external AI agents to use the Research Agent as a specialized research service.

---

# Architecture

The project is being developed as a modular research system.

```text
                         Research Agent
                               │
                               ▼
                       Research Manager
                               │
                               ▼
                        Research Planner
                               │
                               ▼
                          Task Queue
                               │
                               ▼
                         Research Loop
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
          Web Search       Documents        Other Tools
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                       Source Collection
                               │
                               ▼
                      Evidence Extraction
                               │
                               ▼
                       Source Evaluation
                               │
                               ▼
                         Claim Verifier
                               │
                               ▼
                    Contradiction Detection
                               │
                               ▼
                         Synthesizer
                               │
                               ▼
                       Citation Engine
                               │
                               ▼
                      Report Generator
```

The LLM layer is separated from the research workflow:

```text
                     Research Workflow
                            │
                            ▼
                       LLM Gateway
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Claude        Ollama        Gemini
```

Persistent knowledge can eventually be provided through:

```text
                    PostgreSQL
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Research State           pgvector
                                  │
                                  ▼
                         Semantic Retrieval
```

---

# Project Structure

The project is expected to evolve toward a structure similar to:

```text
research-agent/
│
├── app/
│   ├── agent/
│   │   ├── manager.py
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── verifier.py
│   │   └── synthesizer.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── tools/
│   │   ├── search.py
│   │   ├── fetch.py
│   │   ├── pdf.py
│   │   ├── github.py
│   │   └── documents.py
│   │
│   ├── evidence/
│   │   ├── extractor.py
│   │   ├── evaluator.py
│   │   ├── verifier.py
│   │   └── citations.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── anthropic.py
│   │   ├── ollama.py
│   │   ├── gemini.py
│   │   └── router.py
│   │
│   ├── models/
│   │   ├── research.py
│   │   ├── task.py
│   │   ├── source.py
│   │   ├── evidence.py
│   │   └── claim.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── repository.py
│   │
│   └── reporting/
│       ├── markdown.py
│       ├── json.py
│       └── html.py
│
├── tests/
│
├── docs/
│
├── scripts/
│
├── .agent/
│
├── .env.example
├── .gitignore
├── CLAUDE.md
├── README.md
├── pyproject.toml
└── docker-compose.yml
```

The actual structure may change as implementation progresses.

---

# Research Workflow

A typical deep research request will follow this process:

### 1. Receive Research Question

```text
"Compare local LLM frameworks for an AI Assistant Hub."
```

### 2. Analyze Objective

The agent identifies:

* Main objective
* Scope
* Required information
* Potential ambiguities
* Expected output

### 3. Create Research Plan

```text
1. Identify relevant frameworks
2. Compare architecture
3. Compare hardware requirements
4. Compare model support
5. Compare API capabilities
6. Compare agent integration
7. Evaluate limitations
8. Produce recommendation
```

### 4. Execute Research Tasks

Each task generates appropriate queries and collects relevant sources.

### 5. Extract Evidence

Relevant information is converted into structured evidence.

### 6. Evaluate Evidence

Evidence is assessed for reliability, relevance, recency, and corroboration.

### 7. Identify Gaps

The agent determines whether important research questions remain unanswered.

### 8. Iterate

Additional searches are performed when necessary.

### 9. Verify Claims

Important conclusions are checked against the collected evidence.

### 10. Generate Report

The verified evidence is synthesized into a structured report with citations.

---

# Installation

## Requirements

The project requires:

* Python 3.11+
* Git
* An available LLM provider
* Internet access for web research

Additional requirements such as PostgreSQL or Ollama will depend on the enabled features.

## Clone the repository

```bash
git clone <repo-url>

cd research-agent
```

## Create a virtual environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / WSL

```bash
python3 -m venv .venv

source .venv/bin/activate
```

## Install dependencies

During early development:

```bash
pip install -r requirements.txt
```

As the project matures, dependency management may transition to `pyproject.toml`.

---

# Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the required LLM provider and API credentials.

Example:

```env
LLM_PROVIDER=ollama
OLLAMA_ENDPOINT=http://localhost:11434
```

Cloud providers can be enabled through their corresponding environment variables.

**API keys should never be committed to Git.**

---

# Usage

## Basic Research

```bash
research "What is model context protocol?"
```

## Deep Research

```bash
research "Compare LangGraph and CrewAI for production AI agents" --depth deep
```

## Check Research Status

```bash
research status <research-id>
```

## Generate Report

```bash
research report <research-id>
```

## Export

```bash
research export <research-id> --format markdown
```

---

# Development Roadmap

The project will be developed incrementally.

```text
M0  Project Foundation
 ↓
M1  LLM Abstraction
 ↓
M2  Web Search
 ↓
M3  Basic Research Workflow
 ↓
M4  Research Planner + Task Queue
 ↓
M5  Evidence Extraction
 ↓
M6  Citations + Reports
 ↓
M7  Verification + Contradiction Detection
 ↓
M8  LangGraph Workflow
 ↓
M9  Persistent Database
 ↓
M10 Vector Retrieval / RAG
 ↓
M11 Document Research
 ↓
M12 Multi-Provider Gateway
 ↓
M13 Context Management + Failover
 ↓
M14 MCP Service
 ↓
M15 Assistant Hub Integration
 ↓
M16 Evaluation + Observability
 ↓
M17 Production Polish
```

The initial implementation will focus on producing a reliable standalone research agent before adding advanced infrastructure.

---

# Design Principles

### 1. Evidence over generated knowledge

The LLM should interpret collected evidence rather than act as the sole source of truth.

```text
Sources
   ↓
Evidence
   ↓
Claims
   ↓
Verification
   ↓
Report
```

### 2. Modular architecture

Research tools, LLM providers, storage systems, and output formats should be replaceable without rewriting the core agent.

### 3. Provider independence

The research workflow should not depend on a specific model provider.

### 4. Externalized state

Important research state should be stored outside the LLM conversation so tasks can survive context limits, provider failures, and process restarts.

### 5. Auditable research

Important conclusions should be traceable:

```text
Conclusion
    ↓
Claim
    ↓
Evidence
    ↓
Source
```

### 6. Controlled autonomy

The agent should operate autonomously within explicit limits for:

* Search iterations
* Sources
* Runtime
* Token usage
* Tool calls
* Research depth

### 7. Standalone first, composable later

The Research Agent should remain useful as an independent application while exposing clean interfaces for integration into larger agentic systems.

---

# Future Assistant Hub Integration

The Research Agent is intentionally being developed as an independent project.

Once mature, it can become a specialized service within an agentic AI system:

```text
                         Assistant Hub
                              │
                       Intent / Task Router
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    Research Agent       Coding Agent       Automation Agent
          │
          ├── Web Research
          ├── Document Research
          ├── Evidence
          ├── Verification
          └── Reports
```

The Assistant Hub should communicate with the Research Agent through a stable API or MCP interface rather than depending directly on its internal implementation.

This allows the Research Agent to remain independently deployable, testable, and reusable.

---

# Project Vision

The long-term goal is to develop the Research Agent from a simple research assistant into a **reusable autonomous research service** capable of:

* Planning complex investigations
* Conducting multi-step research
* Searching multiple information sources
* Processing user documents
* Maintaining research memory
* Evaluating evidence
* Detecting conflicting information
* Verifying claims
* Producing cited reports
* Recovering from provider failures
* Switching between LLM providers
* Exposing research capabilities through MCP
* Operating as a specialized sub-agent inside larger agentic systems

The final system should behave less like a chatbot that answers questions and more like a **research workflow that uses an LLM as its reasoning component**.

---

## Status

**Current stage:** Initial development

**Target:** Standalone autonomous research agent with CLI, web research, evidence-based synthesis, persistent state, multi-provider support, and MCP integration.

---

*Built as a modular AI-agent project with the goal of later integrating specialized agents into a larger Agentic AI / Assistant Hub architecture.*

*Developed with Claude Code.*
