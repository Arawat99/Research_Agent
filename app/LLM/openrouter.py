'''OpenRouter provider implementation.

This module implements :class:`OpenRouterLLM`, a concrete subclass of
:class:`app.LLM.base.LLMBase` that talks to the OpenRouter API.  It follows the
OpenAI‑compatible chat completion endpoint.  The provider expects an API key
in the ``OPEN_ROUTER`` environment variable.  If the variable is missing the
provider raises :class:`OpenRouterError`.

The implementation uses **httpx** synchronously.  Errors from the network
layer are wrapped in :class:`OpenRouterError` for a stable exception type.
'''

from __future__ import annotations

import os
from typing import List, Dict, Any

import httpx

from .base import LLMBase


class OpenRouterError(RuntimeError):
    """Raised when communication with the OpenRouter API fails."""


class OpenRouterLLM(LLMBase):
    """LLM provider that talks to the OpenRouter API.

    The provider uses the standard OpenAI‑compatible chat completion endpoint at
    ``https://openrouter.ai/api/v1``.  The model identifier should be a valid
    OpenRouter model name such as ``"anthropic/claude-3-5-sonnet"``.
    """

    def __init__(self, model: str, api_key: str | None = None, **_: Any):
        super().__init__(model)
        env_keys = ("OPEN_ROUTER", "OPENROUTER_API_KEY", "OPENAI_API_KEY")
        self.api_key = api_key or next((os.getenv(key) for key in env_keys if os.getenv(key)), None)
        if not self.api_key:
            raise OpenRouterError(
                "OpenRouter API key not found. Set OPEN_ROUTER, OPENROUTER_API_KEY, or OPENAI_API_KEY."
            )
        # Base URL for OpenRouter – use the public API.
        self.base_url = "https://openrouter.ai/api/v1/"
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST *payload* to *path* and decode the JSON response.

        Errors are wrapped in :class:`OpenRouterError`.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Optional headers required by OpenRouter for identification.
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "Claude Research Agent",
        }
        try:
            # Ensure *path* does not start with a slash so that the client joins it with ``base_url``.
            clean_path = path.lstrip('/')
            response = self.client.post(clean_path, json=payload, headers=headers)

            response.raise_for_status()
            try:
                return response.json()
            except Exception as exc:
                raise OpenRouterError(
                    f"Non‑JSON response from OpenRouter {path}: {response.text.strip()}"
                ) from exc
        except Exception as exc:
            raise OpenRouterError(f"Failed OpenRouter request {path}: {exc}") from exc

    def generate(self, prompt: str) -> str:
        """Generate a completion using the chat endpoint with a single user message.

        The OpenRouter chat endpoint returns a ``choices`` list; we extract the
        ``content`` of the first ``message``. Some providers occasionally return
        empty or structurally different payloads (for example ``content=None``),
        so we normalise those cases instead of crashing on a ``NoneType``.
        """
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 512,
            "stream": False,
        }
        data = self._post("chat/completions", payload)

        choices = data.get("choices") or []
        if not choices:
            if data.get("error"):
                msg = data["error"].get("message") if isinstance(data["error"], dict) else str(data["error"])
                raise OpenRouterError(f"OpenRouter returned an error: {msg}")
            raise OpenRouterError("OpenRouter returned no choices in the response")

        message = choices[0].get("message") if isinstance(choices[0], dict) else {}
        content = message.get("content") if isinstance(message, dict) else None

        if isinstance(content, str):
            text = content.strip()
            if text:
                return text

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            combined = "\n".join(parts).strip()
            if combined:
                return combined

        error = data.get("error")
        if error:
            msg = error.get("message") if isinstance(error, dict) else str(error)
            raise OpenRouterError(f"OpenRouter returned an error: {msg}")

        raise OpenRouterError("Unexpected response structure from OpenRouter")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Run a chat completion using the provided *messages* list.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2048,
            "stream": False,
        }
        data = self._post("chat/completions", payload)
        choices = data.get("choices") or []
        if not choices:
            if data.get("error"):
                msg = data["error"].get("message") if isinstance(data["error"], dict) else str(data["error"])
                raise OpenRouterError(f"OpenRouter returned an error: {msg}")
            raise OpenRouterError("Unexpected response structure from OpenRouter chat")

        message = choices[0].get("message") if isinstance(choices[0], dict) else {}
        content = message.get("content") if isinstance(message, dict) else None

        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            if parts:
                return "\n".join(parts).strip()

        raise OpenRouterError("Unexpected response structure from OpenRouter chat")

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass
