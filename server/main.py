"""FastAPI server exposing research jobs and progress over Server-Sent Events."""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Condition, Lock
from typing import Any, Iterator
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agent.research_agent import ResearchAgent


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    model: str = "openrouter/free"
    provider: str | None = None
    max_rounds: int = Field(default=3, ge=1, le=20)
    min_sources: int = Field(default=2, ge=1, le=20)
    num_tasks: int = Field(default=3, ge=1, le=20)


class ResearchJob:
    def __init__(self, request: ResearchRequest):
        self.id = uuid4()
        self.request = request
        self.status = "pending"
        self.answer: str | None = None
        self.error: str | None = None
        self.events: list[dict[str, Any]] = []
        self.condition = Condition()

    def publish(self, event: str, **details: Any) -> None:
        payload = {
            "event": event,
            "job_id": str(self.id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **details,
        }
        with self.condition:
            self.events.append(payload)
            self.condition.notify_all()

    def snapshot(self) -> dict[str, Any]:
        with self.condition:
            return {
                "id": str(self.id),
                "query": self.request.query,
                "status": self.status,
                "answer": self.answer,
                "error": self.error,
                "events": list(self.events),
            }


app = FastAPI(title="Research Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: dict[UUID, ResearchJob] = {}
_jobs_lock = Lock()
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="research")


def _get_job(job_id: UUID) -> ResearchJob:
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research job not found")
    return job


def _run_job(job: ResearchJob) -> None:
    job.status = "in_progress"
    job.publish("started", query=job.request.query)
    try:
        agent = ResearchAgent(model=job.request.model, provider=job.request.provider)
        answer = agent.research(
            job.request.query,
            max_rounds=job.request.max_rounds,
            min_sources=job.request.min_sources,
            num_tasks=job.request.num_tasks,
            progress_callback=lambda update: job.publish(**update),
        )
        job.answer = answer
        job.status = "completed"
        job.publish("completed", answer=answer)
    except Exception as exc:
        job.error = str(exc)
        job.status = "failed"
        job.publish("failed", error=job.error)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/research", status_code=202)
def create_research(request: ResearchRequest) -> dict[str, Any]:
    job = ResearchJob(request)
    with _jobs_lock:
        _jobs[job.id] = job
    _executor.submit(_run_job, job)
    return {"id": str(job.id), "status": job.status, "stream_url": f"/research/{job.id}/stream"}


@app.get("/research/{job_id}")
def get_research(job_id: UUID) -> dict[str, Any]:
    return _get_job(job_id).snapshot()


def _event_stream(job: ResearchJob) -> Iterator[str]:
    index = 0
    while True:
        with job.condition:
            while index >= len(job.events) and job.status not in {"completed", "failed"}:
                job.condition.wait(timeout=15)
            new_events = job.events[index:]
            index = len(job.events)
            finished = job.status in {"completed", "failed"} and index >= len(job.events)

        for event in new_events:
            yield f"event: {event['event']}\ndata: {json.dumps(event)}\n\n"
        if finished:
            return
        if not new_events:
            yield ": keep-alive\n\n"


@app.get("/research/{job_id}/stream")
async def stream_research(job_id: UUID) -> StreamingResponse:
    job = _get_job(job_id)
    return StreamingResponse(
        (line async for line in _async_event_stream(job)),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _async_event_stream(job: ResearchJob):
    iterator = _event_stream(job)
    while True:
        line = await asyncio.to_thread(next, iterator, None)
        if line is None:
            return
        yield line


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=False)