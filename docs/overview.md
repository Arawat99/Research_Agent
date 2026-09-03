# Overview

The Research Agent is a lightweight but practical research workflow for answering questions using structured task execution, web retrieval, and iterative evidence checks rather than a single blind LLM call.

## Current workflow

The agent now follows a queue-based research loop:

```text
User question
    ↓
ResearchPlanner creates subtasks
    ↓
TaskQueue orders work by priority
    ↓
ResearchAgent gathers evidence
    ↓
Check whether enough sources are available
    ├── No → continue with the next queued task or retry search
    └── Yes → synthesize final answer
```

This prevents the agent from running every research sub-question at once and makes the process deterministic and bounded.

## Core components

| Component | Description |
|-----------|-------------|
| `app/LLM` | Provider abstraction and factory for selecting the active LLM backend. The default resolution prefers OpenRouter when an API key is present, then falls back to Ollama or a provider fallback wrapper. |
| `app/agent/planner.py` | `ResearchPlanner` turns a high-level question into a list of smaller research tasks. |
| `app/agent/task_queue.py` | `TaskQueue` orders tasks by priority and exposes next-ready, in-progress, and completion state. |
| `app/agent/research_agent.py` | Runs the actual research loop, gathers search results, checks evidence sufficiency, and returns the final answer. |
| `app/tools/search.py` | Search layer used to fetch candidate sources for a sub-question. |
| `app/tools/fetch.py` | Fetches and normalizes source content from result URLs. |
| `app/models` | Pydantic models for research state, evidence, tasks, and sources. |
| `app/agent/cli.py` | Typer-based command-line interface for interactive use. |
| `server/main.py` | FastAPI job API with background research execution and progress SSE. |
| `server/combined.py` | Single ASGI entrypoint mounting the Gradio UI and FastAPI API together. |
| `frontend` | Gradio interface for starting research and displaying streamed answers and clickable sources. |

## Research loop behavior

The current loop includes two important safeguards:

- It enforces a task queue instead of executing all tasks at once.
- It exits the loop when the agent stops finding new evidence, preventing an endless retry cycle.

This means the system behaves more like a controlled research process than a raw chatbot.

## Source-aware synthesis

The fetch layer preserves structured metadata alongside page text: title, URL,
domain, publication date, retrieval date, snippet, and content. The research
agent includes these fields in the synthesis prompt, allowing the LLM to weigh
source authority and recency instead of seeing an unlabeled block of webpage
text.

For frontend users, the answer is rendered as Markdown so headings, tables,
lists, and fenced code remain readable. Source URLs from completed research
tasks are displayed as clickable links.

## Provider strategy

The LLM router supports:

- `openrouter`
- `ollama`
- `fallback`

The default provider resolution prefers OpenRouter when credentials are present, and falls back to Ollama or a combined fallback provider when appropriate.

## Intended use

The project is designed for evidence-based research tasks where the answer needs more than a single prompt response, including:

- decomposing questions into smaller tasks
- gathering web evidence from multiple references
- checking whether enough sources exist
- answering only after the evidence threshold is met

---

*Updated to match the current queue-driven research loop.*