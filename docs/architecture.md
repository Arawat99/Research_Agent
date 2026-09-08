# Agent Architecture

The research workflow is organized as a small set of replaceable components.

```text
User query
   |
   v
ResearchAgent (orchestrator)
   |
   +--> Planner ------------> ResearchTask[]
   |
   +--> TaskQueue ----------> ordered task execution
   |
   +--> SourceCollector ----> normalized source records
   |
   +--> AnswerGenerator ----> grounded final answer
```

## Why this structure?

`ResearchAgent` is responsible for **workflow decisions**, not provider details.
The concrete implementation is injected through small `Protocol` contracts in
`app/agent/interfaces.py`.

This gives the project three useful properties:

- **Readable:** each class has one obvious responsibility.
- **Testable:** the planner, collector, and generator can be replaced with fakes.
- **Extensible:** a different search backend, local model, or synthesis strategy
  can be added without rewriting the orchestration loop.

## Component responsibilities

| Component | Responsibility |
| --- | --- |
| `ResearchAgent` | Coordinates the workflow and stopping conditions. |
| `ResearchPlanner` | Converts a high-level question into research tasks. |
| `TaskQueue` | Provides deterministic priority-based task execution. |
| `WebSourceCollector` | Searches and fetches web sources, then normalizes them. |
| `LLMAnswerGenerator` | Encapsulates model calls and optional streaming. |
| `get_llm` | Selects concrete LLM providers through an explicit registry. |

The public `ResearchAgent` API remains compatible with the existing `ask`,
`research`, and `run_task_queue` entry points.
