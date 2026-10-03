from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from aavc.jobs.cancellation import CancellationToken


class JobState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class JobSnapshot:
    job_id: str
    name: str
    state: JobState
    error: str | None = None


class BackgroundJob[T]:
    def __init__(self, job_id: str, name: str, token: CancellationToken) -> None:
        self.job_id = job_id
        self.name = name
        self.token = token
        self.state = JobState.PENDING
        self.result: T | None = None
        self.error: str | None = None

    def snapshot(self) -> JobSnapshot:
        return JobSnapshot(
            job_id=self.job_id,
            name=self.name,
            state=self.state,
            error=self.error,
        )
