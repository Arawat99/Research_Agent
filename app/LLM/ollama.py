'''Ollama provider implementation.

This module implements :class:`OllamaLLM`, a concrete subclass of
:class:`app.LLM.base.LLMBase` that talks to an Ollama server via the HTTP
API.  Ollama typically runs locally on ``http://localhost:11434``.

The implementation uses **httpx** in synchronous mode – the rest of the
project is simple and does not need asynchronous I/O.  Errors from the
network layer are wrapped in :class:`OllamaError` to give callers a stable
exception type.

Only the ``generate`` and ``chat`` endpoints are covered.  The ``generate``
endpoint is a thin wrapper around Ollama's ``/api/generate`` call while the
``chat`` method uses ``/api/chat`` which supports a richer message format.
'''

from __future__ import annotations

import os
from typing import List, Dict, Any

import httpx

from .base import LLMBase


class OllamaError(RuntimeError):
    """Raised when communication with the Ollama server fails."""


class OllamaLLM(LLMBase):
    """LLM provider that talks to an Ollama server.

    The default endpoint is ``http://localhost:11434`` but can be
    overridden with the ``OLLAMA_ENDPOINT`` environment variable.  The
    provider expects the server to support the standard Ollama JSON API.
    """

    def __init__(self, model: str, endpoint: str | None = None):
        super().__init__(model)
        self.endpoint = endpoint or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        # A short‑lived client – we could reuse a session for many calls but
        # the overhead is negligible for the expected usage pattern.
        self.client = httpx.Client(base_url=self.endpoint, timeout=30.0)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to POST *payload* to *path* and decode JSON.

        Errors from the HTTP request or a non‑200 status are wrapped in
        :class:`OllamaError`. Non‑JSON responses are also surfaced with their
        raw text so the caller can see the underlying error.
        """
        import json
        try:
            response = self.client.post(path, json=payload)
            response.raise_for_status()
            try:
                return response.json()
            except json.JSONDecodeError:
                # Ollama sometimes returns plain‑text error messages when a model
                # is missing or the request is malformed. Include the raw text
                # in the exception for easier debugging.
                raise OllamaError(
                    f"Ollama endpoint {path} returned non‑JSON response: {response.text.strip()}"
                ) from None
        except Exception as exc:
            raise OllamaError(f"Failed to call Ollama endpoint {path}: {exc}") from exc

    def generate(self, prompt: str) -> str:
        """Generate a completion for *prompt* using Ollama's ``/api/generate``.

        The request payload follows Ollama's specifications – ``model`` and
        ``prompt`` are required.  Additional parameters such as ``temperature``
        or ``max_length`` can be added later.
        """
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        data = self._post("/api/generate", payload)
        # Ollama returns a single ``response`` field when streaming is disabled.
        if isinstance(data.get("response"), str):
            return data["response"].strip()
        # Fallback – some versions return ``generated_text``
        return str(data.get("generated_text", "")).strip()


    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Run a chat completion via Ollama's ``/api/chat`` endpoint.

        ``messages`` should follow the OpenAI style – each element is a dict
        with a ``role`` (``"system"``, ``"user"``, ``"assistant"``) and a
        ``content`` string.
        """
        payload = {"model": self.model, "messages": messages, "stream": False}
        data = self._post("/api/chat", payload)
        # Ollama returns ``message`` with a ``content`` field.
        message = data.get("message")
        if isinstance(message, dict):
            return str(message.get("content", "")).strip()
        # Some older versions may return ``response`` directly.
        if isinstance(message, str):
            return message.strip()
        return ""

    def __del__(self):
        # Ensure the underlying HTTP client releases its resources.
        try:
            self.client.close()
        except Exception:
            pass
