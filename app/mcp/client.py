"""Thin FastMCP client wrapper used by the MCP search adapters.

The research pipeline is synchronous, so the async FastMCP client is driven to
completion inside :func:`run_tool`.  Two ways of returning results are handled
symmetrically: servers that expose structured content (Puri.li) and servers
that return the payload as JSON text (arxiv-mcp-server).
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT


class SearchError(RuntimeError):
    """Raised when a tool call through an MCP search server fails."""


def extract_payload(result: Any) -> Any:
    """Return the structured payload of a tool result.

    ``structured_content`` is preferred when the server supplies it (Puri.li).
    Some servers (arxiv-mcp-server) only attach JSON text to the ``content``
    blocks, which is parsed here.
    """
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured

    text = _result_text(result)
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _result_text(result: Any) -> str:
    """Concatenate the text content blocks of a tool result."""
    parts = []
    for part in getattr(result, "content", []) or []:
        if getattr(part, "type", "") == "text":
            parts.append(getattr(part, "text", "") or "")
    return "".join(parts)


async def _call_tool(
    transport: ClientTransportT,
    tool_name: str,
    arguments: dict[str, Any],
    timeout: float,
) -> Any:
    """Open a client on *transport*, call *tool_name*, and return its payload."""
    async with Client(transport, timeout=timeout) as client:
        result = await client.call_tool(tool_name, arguments)
        if getattr(result, "is_error", False):
            detail = _result_text(result).strip() or "unknown error"
            raise SearchError(f"MCP tool {tool_name} returned an error: {detail[:300]}")
        payload = extract_payload(result)
        if payload is None:
            raise SearchError(f"MCP tool {tool_name} returned no usable payload")
        return payload


def _has_running_loop() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def run_tool(
    transport: ClientTransportT,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    timeout: float = 30.0,
) -> Any:
    """Call an MCP tool synchronously and return its structured payload.

    ``asyncio.run`` needs a fresh event loop; when the caller already lives
    inside one (e.g. a FastAPI handler) the call is executed in a worker thread
    so the loops are not nested.
    """
    def execute() -> Any:
        try:
            return asyncio.run(_call_tool(transport, tool_name, arguments, timeout))
        except SearchError:
            raise
        except Exception as exc:
            raise SearchError(f"MCP tool {tool_name} failed: {exc}") from exc

    if not _has_running_loop():
        return execute()

    outcome: dict[str, Any] = {}

    def worker() -> None:
        try:
            outcome["value"] = execute()
        except BaseException as exc:  # noqa: BLE001 -- propagated to caller below
            outcome["error"] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout + 15.0)
    if thread.is_alive():
        raise SearchError(f"MCP tool {tool_name} timed out")
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]