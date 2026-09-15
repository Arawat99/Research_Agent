# Usage Guide

## Activate the project environment

This project expects to run inside a virtual environment:

```bash
source venv/bin/activate
```

## Use the agent as a Python library

```python
from app.agent import ResearchAgent

agent = ResearchAgent(model="openrouter/free")
answer = agent.ask("What is the tallest mountain on Earth?")
print(answer)
```

The agent will attempt lightweight web grounding for research-style prompts and pass the retrieved sources into the LLM prompt when they are available.

Fetched sources include title, URL, domain, publication date when available,
retrieval date, snippet, and page content. The final prompt includes this
metadata so the model can prefer recent and authoritative evidence.

## Run the iterative research loop

The current agent supports a queue-driven research method that plans subtasks and gathers evidence until enough sources exist:

```python
from app.agent import ResearchAgent

agent = ResearchAgent(model="openrouter/free")
answer = agent.research(
    "What is the impact of AI on software engineering teams?",
    max_rounds=3,
    min_sources=2,
    num_tasks=3,
)
print(answer)
```

To observe progress while the research loop runs, provide a callback:

```python
def on_progress(event):
    print(event["event"], event)

answer = agent.research(
    "What is the impact of AI on software engineering teams?",
    progress_callback=on_progress,
)
```

This is the recommended path for multi-step research because it uses a task queue rather than injecting a single raw prompt into the model.

## Provider configuration

Set the provider through environment variables or pass it directly when creating the agent.

### OpenRouter

```bash
export OPENROUTER_API_KEY="your-key"
export LLM_PROVIDER=openrouter
```

### Ollama

```bash
export LLM_PROVIDER=ollama
export OLLAMA_ENDPOINT=http://localhost:11434
```

### Direct per-instance override

```python
agent = ResearchAgent(model="openrouter/free", provider="openrouter")
```

## MCP search providers

The default search backend scrapes DuckDuckGo. For stronger coverage, the
`app.mcp` package adapts **MCP search servers** to the same
`search_backend` interface the agent already accepts:

- **Puri.li** (`app/mcp/purili.py`) — hosted MCP web search over streamable
  HTTP, no API key, with its own independent index. Also offers
  `search_domain` for restricting results to one site.
- **arxiv-mcp-server** (`app/mcp/arxiv.py`) — local stdio server that searches
  the arXiv API (no API key) and enforces arXiv's ~3-second rate limit.

No code changes are needed in the pipeline; pass the adapters in directly:

```python
from app.mcp import arxiv_search, fallback_search, web_search

# Use Puri.li as the primary backend:
agent = ResearchAgent(model="openrouter/free", search_backend=web_search)

# Try Puri.li, then arxiv, then the built-in DuckDuckGo search:
from app.tools.search import web_search as ddg_search

agent = ResearchAgent(
    model="openrouter/free",
    search_backend=fallback_search(web_search, arxiv_search, ddg_search),
)
```

### Merge results instead of falling back

When more evidence beats a single backend's coverage, `union_search` runs
every backend and merges the results (deduplicated by URL, capped at
`max_results`):

```python
from app.mcp import arxiv_search, union_search, web_search

# Combine Puri.li general web + arXiv papers in one result set:
agent = ResearchAgent(model="openrouter/free",
                      search_backend=union_search(web_search, arxiv_search))
```

### Recover page content via Puri.li

A bare search snippet is not always enough to ground a claim. The collector
keeps richer content in three ways — inline (e.g. an arXiv abstract attached
to the result), a direct page fetch, and a content fallback such as Puri.li's
`get_context` for pages a plain HTTP fetch cannot read:

```python
from app.agent import ResearchAgent
from app.mcp import web_search, get_context

# Fall back to Puri.li's stored copy when the page itself cannot be fetched:
agent = ResearchAgent(
    model="openrouter/free",
    content_backend=get_context,
)
```

### Scope-aware searching

Backends that accept extra keywords (e.g. arXiv's `sort_by`/`categories`) can
be scoped per query without the agent hard-coding one backend. Pass a scope
through the collector, and it forwards only the keys the backend understands:

```python
agent = ResearchAgent(
    model="openrouter/free",
    search_backend=arxiv_search,
    search_scope={"domain": "arxiv.org"},          # example, see arxiv signature
)

# Or per-query on the underlying collector:
collector.collect("query", scope={"categories": ["cs.AI"], "sort_by": "date"})
```

Scope keys a backend does not accept are dropped, so a plain DuckDuckGo
backend is never handed arguments it does not understand.

### Install the arXiv server

Puri.li needs nothing to install; the arXiv adapter needs the local server on
`PATH` (install once):

```bash
pip install uv
uv tool install arxiv-mcp-server
```

If the binary is not on `PATH`, point the adapter at it or use another launcher:

```bash
export ARXIV_COMMAND="/home/you/.local/bin/arxiv-mcp-server"   # or "uvx"
```

### Configuration

```text
PURLI_URL            Puri.li MCP endpoint            (default https://puri.li/mcp)
PURLI_SEARCH_TIMEOUT Puri.li timeout seconds         (default 30)
ARXIV_COMMAND        arxiv-mcp-server executable     (default arxiv-mcp-server)
ARXIV_SEARCH_TIMEOUT arXiv stdio timeout seconds     (default 60)
```

### Behaviour

- Results are normalised to `[{title, url, snippet}]`, the same shape all
  other backends produce, so deduplication and evidence scoring are unchanged.
- arXiv papers use their abstract page URL (`https://arxiv.org/abs/...`) so the
  normal page-fetching step can read them.
- Like the built-in search, transient failures degrade to an empty list instead
  of raising, so the research loop can fall back to another backend.

## Command line usage

Run the CLI from the project root:

```bash
source venv/bin/activate
research "Explain the concept of memoization." 
```

### CLI options

- `--model` – model identifier to use
- `--provider` – provider override such as `openrouter` or `ollama`

## Guardrails in the research loop

The research loop is deliberately bounded:

- it stops when the task queue is empty
- it stops when evidence is sufficient
- it stops when no new sources are found for multiple rounds

This avoids endless retries while still allowing the agent to continue searching if more evidence is required.

## Running tests

```bash
source venv/bin/activate
python -m unittest discover -s tests -q
```

## Run the HTTP API and Gradio UI

For separate local processes:

```bash
python -m server.main
python frontend/app.py
```

For one local process serving both the API and frontend:

```bash
uvicorn server.combined:app --host 0.0.0.0 --port 5000
```

Open `http://127.0.0.1:5000`. The combined service exposes the Gradio UI at
`/`, JSON job snapshots at `/research/{id}`, and progress SSE at
`/research/{id}/stream`.

## Deploy as one Render service

Use the repository root as the service directory:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn server.combined:app --host 0.0.0.0 --port $PORT
```

Set LLM credentials as Render environment secrets. The combined app uses the
Render-provided port for both the frontend and backend.

---

*Updated to reflect the queued, iterative research workflow and the current provider defaults.*