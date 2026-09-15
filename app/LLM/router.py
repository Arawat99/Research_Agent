"""Provider registry and factory for the project's LLM abstraction."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from .base import LLMBase
from .ollama import OllamaLLM
from .openrouter import OpenRouterLLM
from .xkiro import XkiroLLM


ProviderFactory = Callable[[str], LLMBase]

# Free-tier xKiro model used when the caller's model id cannot reach the account.
# Paid/premium xKiro models (e.g. "openai/gpt-5.6-sol") return HTTP 403 for
# accounts funded with promotional credits, and the shared app default
# ("openrouter/free") is an OpenRouter id that xKiro does not recognise.
XKIRO_DEFAULT_MODEL = "qwen/qwen3.7-plus:free"


def _resolve_xkiro_model(model: str) -> str:
    """Pick a model id the xKiro account can serve.

    Explicit ``vendor/model`` ids are honored unchanged.  The app's OpenRouter
    flavoured default is substituted with a free-tier xKiro model.
    """
    if model and model != "openrouter/free" and "/" in model:
        return model
    return XKIRO_DEFAULT_MODEL


def _provider_factories(**kwargs: Any) -> dict[str, ProviderFactory]:
    """Return the concrete provider constructors supported by the application."""
    return {
        "ollama": lambda model: OllamaLLM(model, **kwargs),
        "openrouter": lambda model: OpenRouterLLM(model, **kwargs),
        "xkiro": lambda model: XkiroLLM(_resolve_xkiro_model(model), **kwargs),
    }


class FallbackLLM(LLMBase):
    """Try configured providers in order until one returns successfully."""

    def __init__(self, model: str, providers: list[LLMBase]):
        super().__init__(model)
        if not providers:
            raise ValueError("No valid LLM providers available for fallback")
        self.providers = providers

    def _run(self, method: str, *args: Any, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                response = getattr(provider, method)(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                continue

            # A provider that returns an empty or whitespace-only response is
            # degraded, not successful.  Moving on gives the next provider a
            # chance instead of returning blank output as a valid answer.
            if isinstance(response, str) and response.strip():
                return response

        if last_error:
            raise last_error
        raise RuntimeError("No LLM provider returned a usable response")

    def generate(self, prompt: str) -> str:
        return self._run("generate", prompt)

    def chat(self, messages: list[dict[str, Any]]) -> str:
        return self._run("chat", messages)


def _build_fallback(model: str, **kwargs: Any) -> FallbackLLM:
    """Construct available providers without failing during optional setup."""
    providers: list[LLMBase] = []
    # xKiro is the primary provider; the remaining entries are failover targets
    # tried in order when an earlier provider is unavailable or degraded.  xKiro
    # receives a free-tier model id rather than the shared app default.
    for factory in (
        lambda: XkiroLLM(_resolve_xkiro_model(model), **kwargs),
        lambda: OpenRouterLLM(model, **kwargs),
        lambda: OllamaLLM(model, **kwargs),
    ):
        try:
            providers.append(factory())
        except Exception:
            continue
    return FallbackLLM(model, providers)


def _resolve_default_provider() -> str:
    """Resolve provider configuration from the environment."""
    configured = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    if configured:
        return configured

    if any(os.getenv(key) for key in ("OPEN_ROUTER", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "XKIRO_API_KEY")):
        return "fallback"
    if os.getenv("OLLAMA_ENDPOINT"):
        return "ollama"
    return "fallback"


def get_llm(model: str, provider: str | None = None, **kwargs: Any) -> LLMBase:
    """Return a provider selected explicitly or from runtime configuration."""
    selected = (provider or _resolve_default_provider()).strip().lower()

    if selected == "fallback":
        return _build_fallback(model, **kwargs)

    factories = _provider_factories(**kwargs)
    try:
        return factories[selected](model)
    except KeyError as exc:
        supported = ", ".join(sorted((*factories, "fallback")))
        raise ValueError(f"Unsupported LLM provider '{selected}'. Supported: {supported}") from exc
