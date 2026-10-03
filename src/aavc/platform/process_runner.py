from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


class ProcessTimeoutError(RuntimeError):
    def __init__(self, timeout_seconds: float) -> None:
        super().__init__(f"Child process timed out after {timeout_seconds:.3f} seconds")
        self.timeout_seconds = timeout_seconds


class ProcessLaunchError(RuntimeError):
    pass


class ProcessRunner:
    """The only repository owner allowed to execute child processes."""

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        if not argv:
            raise ValueError("argv must not be empty")
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        try:
            completed = subprocess.run(
                list(argv),
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            assert timeout_seconds is not None
            raise ProcessTimeoutError(timeout_seconds) from None
        except OSError as exc:
            executable = argv[0]
            raise ProcessLaunchError(
                f"Unable to launch child process '{executable}': {type(exc).__name__}"
            ) from None
        return ProcessResult(completed.returncode, completed.stdout, completed.stderr)
