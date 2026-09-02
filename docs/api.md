# API Reference

## `app.agent.research_agent.ResearchAgent`

```python
class ResearchAgent:
    def __init__(self, model: str = "openrouter/free", provider: str | None = None):
        ...

    def ask(self, query: str) -> str:
        """Run a direct LLM answer for a query."""
        ...

    def research(
        self,
        query: str,
        max_rounds: int = 3,
        min_sources: int = 2,
        num_tasks: int = 3,
    ) -> str:
        """Run the queue-based research loop until enough evidence is found."""
        ...

    def run_task_queue(
        self,
        tasks: list[ResearchTask],
        worker: Callable[[ResearchTask], object] | None = None,
    ) -> list[tuple[ResearchTask, object]]:
        """Execute queued tasks in priority order."""
        ...
```

### `ask(query: str) -> str`

Performs a direct answer request to the configured LLM. If the query looks like a research prompt, the agent may use the search and fetch tools to add web grounding before calling the model.

### `research(query, max_rounds=3, min_sources=2, num_tasks=3) -> str`

Runs the iterative research workflow:

1. create a research plan
2. enqueue tasks by priority
3. fetch sources for the next task
4. collect evidence
5. stop once enough evidence is found or no new evidence is available
6. synthesize the final answer

### `run_task_queue(...)`

Executes tasks in priority order and returns a list of `(task, output)` tuples.

## `app.agent.planner.ResearchPlanner`

```python
planner = ResearchPlanner(model="openrouter/free")
tasks = planner.create_plan("What is the role of AI in software testing?", num_tasks=3)
```

`ResearchPlanner.create_plan(...)` returns a list of `ResearchTask` objects.

## `app.agent.task_queue.TaskQueue`

The task queue maintains a deterministic ordering and enforces task state transitions:

- `PENDING`
- `IN_PROGRESS`
- `COMPLETED`
- `FAILED`

Tasks are selected by priority and are processed in sequence so the agent does not fire all research actions at once.

## LLM selection

The router is exposed via:

```python
from app.LLM import get_llm
llm = get_llm(model="openrouter/free")
```

Supported providers include:

- `openrouter`
- `ollama`
- `fallback`

---

*Documentation updated to match the current research-loop implementation and provider selection logic.*