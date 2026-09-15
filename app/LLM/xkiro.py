'''xKiro provider implementation.

This module implements :class:`XkiroLLM`, a concrete subclass of
:class:`app.LLM.base.LLMBase` that talks to the xKiro API.  xKiro is a unified
API gateway that proxies OpenAI-compatible chat completion requests to upstream
providers with automatic failover.  The provider expects an API key in the
``XKIRO_API_KEY`` environment variable.  If the variable is missing the provider
raises :class:`XkiroError`.

The implementation uses **httpx** synchronously.  Errors from the network
layer are wrapped in :class:`XkiroError` for a stable exception type.
'''

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from typing import Any, Dict, List

import httpx

from .base import LLMBase


class XkiroError(RuntimeError):
    """Raised when communication with the xKiro API fails."""


class XkiroLLM(LLMBase):
    """LLM provider that talks to the xKiro API.

    The provider uses the OpenAI-compatible chat completion endpoint at
    ``https://api.xkiro.com/v1``.  The model identifier should use xKiro's
    ``vendor/model`` format, e.g. ``"openai/gpt-5.6-sol"``.
    """

    def __init__(self, model: str, api_key: str | None = None, **_: Any):
        super().__init__(model)
        self.api_key = api_key or os.getenv("XKIRO_API_KEY")
        if not self.api_key:
            raise XkiroError(
                "xKiro API key not found. Set XKIRO_API_KEY."
            )
        # Base URL for xKiro – use the public API.
        self.base_url = "https://api.xkiro.com/v1/"
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST *payload* to *path* and decode the JSON response.

        Errors are wrapped in :class:`XkiroError`.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            # Ensure *path* does not start with a slash so that the client joins it with ``base_url``.
            clean_path = path.lstrip('/')
            response = self.client.post(clean_path, json=payload, headers=headers)

            # raise_for_status() would discard the API's JSON error body (e.g. the
            # 403 explaining that a premium model needs a paid plan), so surface
            # the reason from the response body directly.
            if response.is_error:
                detail = response.text.strip()
                suffix = f": {detail[:300]}" if detail else ""
                raise XkiroError(
                    f"xKiro request {path} returned HTTP {response.status_code}{suffix}"
                )

            try:
                return response.json()
            except Exception as exc:
                raise XkiroError(
                    f"Non-JSON response from xKiro {path}: {response.text.strip()}"
                ) from exc
        except XkiroError:
            raise
        except Exception as exc:
            raise XkiroError(f"Failed xKiro request {path}: {exc}") from exc

    def generate(self, prompt: str) -> str:
        """Generate a completion using the chat endpoint with a single user message.

        The xKiro chat endpoint returns a ``choices`` list; we extract the
        ``content`` of the first ``message``.  Some upstream providers
        occasionally return empty or structurally different payloads (for
        example ``content=None``), so we normalise those cases instead of
        crashing on a ``NoneType``.
        """
        messages = [{"role": "user", "content": prompt}]
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
                raise XkiroError(f"xKiro returned an error: {msg}")
            raise XkiroError("xKiro returned no choices in the response")

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
            raise XkiroError(f"xKiro returned an error: {msg}")

        raise XkiroError("Unexpected response structure from xKiro")

    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Yield answer text chunks from xKiro's SSE completion stream."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            with self.client.stream("POST", "chat/completions", json=payload, headers=headers) as response:
                if response.is_error:
                    detail = response.text.strip()
                    suffix = f": {detail[:300]}" if detail else ""
                    raise XkiroError(
                        f"xKiro streaming request returned HTTP {response.status_code}{suffix}"
                    )
                for line in response.iter_lines():
                    if not line or line == "data: [DONE]":
                        continue
                    data = json.loads(line.removeprefix("data: ").strip())
                    delta = ((data.get("choices") or [{}])[0].get("delta") or {}).get("content")
                    if isinstance(delta, str) and delta:
                        yield delta
        except XkiroError:
            raise
        except Exception as exc:
            raise XkiroError(f"Failed xKiro streaming request: {exc}") from exc

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
                raise XkiroError(f"xKiro returned an error: {msg}")
            raise XkiroError("Unexpected response structure from xKiro chat")

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

        raise XkiroError("Unexpected response structure from xKiro chat")

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass