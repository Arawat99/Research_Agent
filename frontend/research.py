"""Research job actions and progress presentation helpers."""

from __future__ import annotations

import html
import time
from typing import Any

import gradio as gr

from .api import request_json


def status_label(status: str) -> str:
    labels = {
        "pending": "Pending",
        "running": "Researching",
        "completed": "Completed",
        "failed": "Failed",
    }
    return labels.get(status, status.replace("_", " ").title())


def progress_html(snapshot: dict[str, Any]) -> str:
    events = snapshot.get("events", [])
    if not events:
        return """
        <div class="progress-empty">
            <div class="empty-icon">⌁</div>
            <div>
                <strong>Waiting for research to begin</strong>
                <span>The research agent will show its process here.</span>
            </div>
        </div>
        """

    rows = []
    for event in events:
        event_type = event.get("event", "")
        if event_type == "task_started":
            title, description, icon, css_class = (
                "Research task started",
                event.get("question", "Research task"),
                "→",
                "progress-active",
            )
        elif event_type == "task_completed":
            sources = int(event.get("sources_found", 0))
            title = "Research task completed"
            description = f"{event.get('question', 'Research task')} <span class='event-meta'>{sources} source(s)</span>"
            icon, css_class = "✓", "progress-completed"
        elif event_type == "started":
            title, description, icon, css_class = "Research started", event.get("query", "Preparing research"), "◉", "progress-active"
        elif event_type == "planned":
            title, description, icon, css_class = "Research plan created", event.get("query", "Planning research"), "◆", "progress-active"
        elif event_type == "finalizing":
            title, description, icon, css_class = "Finalizing answer", event.get("query", "Preparing final answer"), "✦", "progress-active"
        else:
            continue

        rows.append(f"""
        <div class="progress-item {css_class}">
            <div class="progress-icon">{icon}</div>
            <div class="progress-content">
                <div class="progress-title">{html.escape(title)}</div>
                <div class="progress-description">{html.escape(description)}</div>
            </div>
        </div>
        """)
    return "".join(rows)


def sources_html(snapshot: dict[str, Any]) -> str:
    completed = [event for event in snapshot.get("events", []) if event.get("event") == "task_completed"]
    total = sum(int(event.get("sources_found", 0)) for event in completed)
    source_rows = []
    for event in completed:
        for source in event.get("sources", []):
            url = source.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                continue
            title = html.escape(source.get("title") or url)
            safe_url = html.escape(url, quote=True)
            source_rows.append(f"""
        <div class="source-row">
            <div class="source-dot"></div>
            <a class="source-link" href="{safe_url}" target="_blank" rel="noopener noreferrer">{title}</a>
        </div>
        """)

    if not source_rows:
        return """
        <div class="source-empty">
            <div class="source-empty-icon">◎</div>
            <span>No source links available yet.</span>
        </div>
        """

    return f"""
    <div class="source-total">
        <div class="source-total-number">{total}</div>
        <div><strong>Sources collected</strong><span>Across research tasks</span></div>
    </div>
    <div class="source-tasks">{''.join(source_rows)}</div>
    """


def start_research(query: str, model: str, max_rounds: int, min_sources: int, num_tasks: int):
    if not query.strip():
        raise gr.Error("Enter a research question first.")
    job = request_json("POST", "/research", json={
        "query": query.strip(),
        "model": model,
        "max_rounds": int(max_rounds),
        "min_sources": int(min_sources),
        "num_tasks": int(num_tasks),
    })
    return (
        job["id"],
        "Researching",
        progress_html({}),
        "Your evidence-based answer will appear here.",
        sources_html({}),
        "",
    )


def follow_research(job_id: str):
    if not job_id:
        return
    while True:
        try:
            snapshot = request_json("GET", f"/research/{job_id}")
        except RuntimeError as exc:
            yield [], "Service connection lost", str(exc), "Sources unavailable", ""
            return

        answer = snapshot.get("answer") or "The research answer will appear here when synthesis is complete."
        yield (
            progress_html(snapshot),
            status_label(snapshot.get("status", "pending")),
            answer,
            sources_html(snapshot),
            snapshot.get("error") or "",
        )
        if snapshot.get("status") in {"completed", "failed"}:
            return
        time.sleep(1)


def reset_research():
    return (
        "",
        "Pending",
        progress_html({}),
        "Your evidence-based answer will appear here.",
        sources_html({}),
        "",
    )
