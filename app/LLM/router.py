'''Router for selecting an LLM provider.

The router inspects environment configuration to decide which concrete
provider class to instantiate.  At the moment we only have an Ollama
implementation, but the design anticipates additional providers such as
OpenRouter in the future.

Usage example::

    from app.LLM import get_llm
    llm = get_llm(model="gpt-oss:120b-cloud")  # provider defaults to OLLAMA
    answer = llm.generate("What is the capital of France?")

If the ``LLM_PROVIDER`` environment variable is set to ``"ollama"`` (the
default) the :class:`~app.LLM.ollama.OllamaLLM` class is used.  When new
providers are added they can be referenced by their own identifier (for
example ``"openrouter"``) and the router will instantiate the appropriate
class.
'''

from __future__ import annotations

import os
from typing import Any

# Import the concrete provider(s).  Import errors are deliberately not
# suppressed – a missing provider is a configuration problem that should
# surface early.
from .ollama import OllamaLLM

# Placeholder for future imports, e.g.:
# from .openrouter import OpenRouterLLM


def _provider_factory(provider_name: str, model: str, **kwargs: Any) -> Any:
    """Return an instantiated provider based on *provider_name*.

    Args:
        provider_name: Identifier of the provider, e.g. ``"ollama"``.
        model: Model name to pass to the provider class.
        **kwargs: Additional keyword arguments forwarded to the provider.
    """
    provider_name = provider_name.lower()
    if provider_name == "ollama":
        return OllamaLLM(model, **kwargs)
    # Future providers can be added here.
    raise ValueError(f"Unsupported LLM provider: {provider_name}")


def get_llm(model: str, provider: str | None = None, **kwargs: Any) -> Any:
    """Factory function that returns a concrete LLM instance.

    The function first checks the *provider* argument; if omitted it falls
    back to the ``LLM_PROVIDER`` environment variable, finally defaulting to
    ``"ollama"``.  Additional provider‑specific keyword arguments can be passed
    through ``**kwargs``.
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "ollama")
    return _provider_factory(provider, model, **kwargs)
