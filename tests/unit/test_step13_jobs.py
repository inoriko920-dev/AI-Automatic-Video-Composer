from __future__ import annotations

from threading import Event

import pytest

from aavc.jobs.cancellation import CancellationToken
from aavc.jobs.job import JobState
from aavc.jobs.manager import JobManager


def test_job_manager_reports_success() -> None:
    with JobManager(max_workers=1) as manager:
        job = manager.submit("success", lambda token: 42 if not token.is_cancelled else 0)
        assert manager.wait(job.job_id, timeout=2.0) == 42
        assert manager.snapshot(job.job_id).state is JobState.SUCCEEDED
        assert job.result == 42


def test_job_manager_cooperative_cancel() -> None:
    started = Event()
    release = Event()

    def work(token: CancellationToken) -> str:
        started.set()
        release.wait(timeout=2.0)
        token.raise_if_cancelled()
        return "done"

    with JobManager(max_workers=1) as manager:
        job = manager.submit("cancel-me", work)
        assert started.wait(timeout=1.0)
        assert manager.cancel(job.job_id) is True
        release.set()
        assert manager.wait(job.job_id, timeout=2.0) is None
        assert manager.snapshot(job.job_id).state is JobState.CANCELLED


def test_job_manager_records_failure() -> None:
    def fail(token: CancellationToken) -> int:
        token.raise_if_cancelled()
        raise ValueError("boom")

    with JobManager(max_workers=1) as manager:
        job = manager.submit("failure", fail)
        with pytest.raises(ValueError, match="boom"):
            manager.wait(job.job_id, timeout=2.0)
        snapshot = manager.snapshot(job.job_id)
        assert snapshot.state is JobState.FAILED
        assert snapshot.error == "ValueError: boom"
