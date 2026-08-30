'''Base abstraction for LLM providers.

This module defines the abstract interface that concrete LLM provider
implementations must follow.  The goal is to give the rest of the code
base a simple, provider‑agnostic way to generate completions or perform a
chat conversation.

Typical usage:

    from app.LLM import get_llm
    llm = get_llm(model="gpt-oss:120b-cloud", provider="ollama")
    response = llm.generate("Explain the importance of abstraction.")

The `generate` method is a convenience wrapper around a single‑prompt call.
For richer interactions, the `chat` method accepts a list of message
objects following the OpenAI/Anthropic schema (``{"role": "user", ...}``).

Only the methods required for the current project are defined – they can be
extended later without breaking existing callers.
'''

from __future__ import annotations

import abc
from typing import List, Dict, Any


class LLMBase(abc.ABC):
    """Abstract base class for LLM providers.

    Sub‑classes must implement two primary methods:

    * :meth:`generate` – generate a completion from a single prompt string.
    * :meth:`chat` – run a chat session given a list of message dictionaries.

    Both methods return the model's textual response.
    """

    def __init__(self, model: str):
        """Create a new provider instance.

        Args:
            model: The identifier of the model to use (e.g. ``"gpt-oss:120b-cloud"``).
        """
        self.model = model

    @abc.abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a completion for *prompt*.

        Args:
            prompt: The prompt text to send to the model.

        Returns:
            The model's completion as a plain string.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Perform a chat completion.

        Args:
            messages: A list of message dictionaries with at least ``role``
                (``"user"``, ``"assistant"`` or ``"system"``) and ``content``.

        Returns:
            The model's reply as a plain string.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"
