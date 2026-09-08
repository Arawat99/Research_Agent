"""LLM-backed answer generation for the research agent."""

from __future__ import annotations

from collections.abc import Callable

from app.LLM import get_llm
from app.LLM.openrouter import OpenRouterError
from app.prompts.loader import add_system_prompt, load_prompts


class LLMAnswerGenerator:
    """Generate answers through the project's provider-agnostic LLM interface."""

    def __init__(self, model: str = "openrouter/free", provider: str | None = None):
        self.llm = get_llm(model=model, provider=provider)
        self.system_prompt = load_prompts()

    def generate(
        self,
        prompt: str,
        *,
        progress_callback: Callable[[dict[str, object]], None] | None = None,
    ) -> str:
        """Generate a response and optionally emit streamed answer deltas."""
        try:
            if progress_callback is not None and hasattr(self.llm, "generate_stream"):
                chunks: list[str] = []
                for chunk in self.llm.generate_stream(add_system_prompt(prompt, self.system_prompt)):
                    chunks.append(chunk)
                    progress_callback({"event": "answer_delta", "delta": chunk})
                answer = "".join(chunks).strip()
                if answer:
                    return answer

            return self.llm.generate(add_system_prompt(prompt, self.system_prompt))
        except OpenRouterError as exc:
            return (
                "I could not get a valid model response from the configured provider. "
                f"Provider error: {exc}"
            )
        except Exception as exc:
            return f"I could not complete the model call due to a provider failure. Details: {exc}"
