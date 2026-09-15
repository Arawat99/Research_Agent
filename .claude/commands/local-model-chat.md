---
description: Send a prompt to the local Ollama model through the project helper script.
---

Use the local model helper to answer a focused question or task.

Run:

```bash
python3 scripts/ollama_chat.py "<your prompt here>"
```

Use this for:

- quick summaries
- project analysis
- note cleanup
- brainstorming
- local research assistance

If the model is not available, first check the Ollama status with:

```bash
python3 scripts/ollama_status.py
```

Then explain the result clearly and suggest the next step if the model is not ready.
