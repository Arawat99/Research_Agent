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

from .base import LLMBase

# suppressed – a missing provider is a configuration problem that should
# surface early.
from .ollama import OllamaLLM

# Placeholder for future imports, e.g.:
# from .openrouter import OpenRouterLLM
from .openrouter import OpenRouterLLM


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
    if provider_name == "openrouter":
        return OpenRouterLLM(model, **kwargs)
    if provider_name == "fallback":
        # Fallback provider: try ollama first, then openrouter.
        # We construct a simple wrapper that attempts each in order.
        class FallbackLLM(LLMBase):
            def __init__(self, model: str, **kw):
                super().__init__(model)
                self.providers = []
                # Instantiate primary (ollama) – ignore errors during construction.
                try:
                    self.providers.append(OllamaLLM(model, **kw))
                except Exception:
                    pass
                try:
                    self.providers.append(OpenRouterLLM(model, **kw))
                except Exception:
                    pass
                if not self.providers:
                    raise ValueError("No valid LLM providers available for fallback")

            def _run(self, method: str, *args, **kwargs):
                last_exc = None
                for prov in self.providers:
                    try:
                        return getattr(prov, method)(*args, **kwargs)
                    except Exception as exc:
                        last_exc = exc
                if last_exc:
                    raise last_exc
                raise RuntimeError("FallbackLLM failed without exception")

            def generate(self, prompt: str) -> str:
                return self._run("generate", prompt)

            def chat(self, messages):
                return self._run("chat", messages)

        return FallbackLLM(model, **kwargs)
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
