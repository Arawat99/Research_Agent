"""Load the agent's prompt instructions from the prompts directory."""

from __future__ import annotations

from pathlib import Path


PROMPT_SUFFIXES = {".md", ".txt"}
PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompts(prompt_dir: Path = PROMPTS_DIR) -> str:
    """Return all supported prompt files in deterministic filename order."""
    prompt_files = sorted(
        path for path in prompt_dir.iterdir()
        if path.is_file() and path.suffix.lower() in PROMPT_SUFFIXES
    )
    prompts = [path.read_text(encoding="utf-8").strip() for path in prompt_files]
    return "\n\n".join(prompt for prompt in prompts if prompt)


def add_system_prompt(prompt: str, system_prompt: str | None = None) -> str:
    """Prefix a task prompt with the configured agent instructions."""
    instructions = system_prompt if system_prompt is not None else load_prompts()
    if not instructions:
        return prompt
    return f"=== SYSTEM INSTRUCTIONS ===\n{instructions}\n\n=== TASK ===\n{prompt}"
