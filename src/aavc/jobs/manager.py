from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from threading import RLock
from typing import Any, TypeVar, cast
from uuid import uuid4

from aavc.jobs.cancellation import CancellationToken, JobCancelledError
from aavc.jobs.job import BackgroundJob, JobSnapshot, JobState

T = TypeVar("T")
JobFunction = Callable[[CancellationToken], T]


class JobManager:
    def __init__(self, *, max_workers: int = 4) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="aavc-job")
        self._jobs: dict[str, BackgroundJob[Any]] = {}
        self._futures: dict[str, Future[Any]] = {}
        self._lock = RLock()
        self._closed = False

    def submit(self, name: str, function: JobFunction[T]) -> BackgroundJob[T]:
        if not name.strip():
            raise ValueError("job name must not be empty")
        with self._lock:
            if self._closed:
                raise RuntimeError("job manager is closed")
            job: BackgroundJob[T] = BackgroundJob(uuid4().hex, name.strip(), CancellationToken())
            self._jobs[job.job_id] = cast(BackgroundJob[Any], job)
            future = self._executor.submit(self._run_job, job, function)
            self._futures[job.job_id] = future
            return job

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise KeyError(job_id)
            if job.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
                return False
            job.token.cancel()
            future = self._futures.get(job_id)
            if future is not None and future.cancel():
                job.state = JobState.CANCELLED
            return True

    def snapshot(self, job_id: str) -> JobSnapshot:
        with self._lock:
            try:
                return self._jobs[job_id].snapshot()
            except KeyError:
                raise KeyError(job_id) from None

    def snapshots(self) -> tuple[JobSnapshot, ...]:
        with self._lock:
            return tuple(job.snapshot() for job in self._jobs.values())

    def wait(self, job_id: str, *, timeout: float | None = None) -> Any:
        with self._lock:
            future = self._futures.get(job_id)
            if future is None:
                raise KeyError(job_id)
        try:
            return future.result(timeout=timeout)
        except JobCancelledError:
            return None

    def shutdown(self, *, wait: bool = True, cancel_pending: bool = True) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            if cancel_pending:
                for job in self._jobs.values():
                    if job.state in {JobState.PENDING, JobState.RUNNING}:
                        job.token.cancel()
        self._executor.shutdown(wait=wait, cancel_futures=cancel_pending)

    def __enter__(self) -> JobManager:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        del exc_type, exc, traceback
        self.shutdown()

    def _run_job(self, job: BackgroundJob[T], function: JobFunction[T]) -> T | None:
        with self._lock:
            if job.token.is_cancelled:
                job.state = JobState.CANCELLED
                return None
            job.state = JobState.RUNNING
        try:
            job.token.raise_if_cancelled()
            result = function(job.token)
            job.token.raise_if_cancelled()
        except JobCancelledError:
            with self._lock:
                job.state = JobState.CANCELLED
                job.error = None
            return None
        except Exception as exc:
            with self._lock:
                job.state = JobState.FAILED
                job.error = f"{type(exc).__name__}: {exc}"
            raise
        with self._lock:
            job.result = result
            job.state = JobState.SUCCEEDED
            job.error = None
        return result
