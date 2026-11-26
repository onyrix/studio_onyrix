"""Single-worker job queue: jobs are serialized (one model instance) and cancellable."""

from __future__ import annotations

import logging
import queue
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.gen.engine import GenerationCancelled

log = logging.getLogger(__name__)

TERMINAL = frozenset({"done", "error", "cancelled"})


@dataclass
class Job:
    id: str
    run: Callable[[Job], dict[str, Any]]
    status: str = "queued"
    events: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        with self._lock:
            self.events.append({"event": event, "data": data or {}})

    def events_since(self, index: int) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.events[index:])

    @property
    def finished(self) -> bool:
        return self.status in TERMINAL

    def summary(self) -> dict[str, Any]:
        return {"id": self.id, "status": self.status, "result": self.result, "error": self.error}


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._queue: queue.Queue[Job | None] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._lock = threading.Lock()

    def submit(self, run: Callable[[Job], dict[str, Any]]) -> Job:
        job = Job(id=uuid.uuid4().hex, run=run)
        job.emit("queued", {"position": self._queue.qsize()})
        with self._lock:
            self._jobs[job.id] = job
            if self._worker is None:
                self._worker = threading.Thread(target=self._loop, name="generation", daemon=True)
                self._worker.start()
        self._queue.put(job)
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> Job | None:
        job = self._jobs.get(job_id)
        if job is not None and not job.finished:
            job.cancel_event.set()
        return job

    def shutdown(self) -> None:
        for job in list(self._jobs.values()):
            job.cancel_event.set()
        if self._worker is not None:
            self._queue.put(None)
            self._worker.join(timeout=5)

    def _loop(self) -> None:
        while True:
            job = self._queue.get()
            if job is None:
                return
            if job.cancel_event.is_set():
                job.status = "cancelled"
                job.emit("cancelled")
                continue
            job.status = "running"
            job.emit("started")
            try:
                job.result = job.run(job)
            except GenerationCancelled:
                job.status = "cancelled"
                job.emit("cancelled")
            except Exception as exc:
                log.exception("job %s failed", job.id)
                job.error = f"{type(exc).__name__}: {exc}"
                job.status = "error"
                job.emit("error", {"message": job.error})
            else:
                job.status = "done"
                job.emit("done", job.result)
