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

---

*Updated to reflect the queued, iterative research workflow and the current provider defaults.*