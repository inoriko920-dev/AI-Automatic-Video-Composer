from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass

WINDOWS_COMMAND_LINE_LIMIT = 32767


def windows_command_line_units(argv: Sequence[str]) -> int:
    """Return CreateProcessW command-line length in UTF-16 code units, including NUL."""

    command_line = subprocess.list2cmdline(list(argv))
    return len(command_line.encode("utf-16-le")) // 2 + 1


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner:
    """The only repository owner allowed to execute child processes."""

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        completed = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
        return ProcessResult(completed.returncode, completed.stdout, completed.stderr)
