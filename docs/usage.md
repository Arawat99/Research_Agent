# Usage Guide

## Activate the project environment

This project expects to run inside a virtual environment:

```bash
cd "/home/chrisjoshua/Personal AI Assistant/projects/research agent"
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