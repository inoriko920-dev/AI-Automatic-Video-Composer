from __future__ import annotations

from dataclasses import dataclass
import subprocess
from collections.abc import Sequence

@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str

class ProcessRunner:
    """The only repository owner allowed to execute child processes."""

    def run(self, argv: Sequence[str], *, timeout_seconds: float | None = None) -> ProcessResult:
        completed = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        return ProcessResult(completed.returncode, completed.stdout, completed.stderr)
