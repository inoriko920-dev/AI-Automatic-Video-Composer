from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aavc.domain.errors import RenderError
from aavc.platform.process_runner import ProcessRunner


@dataclass(frozen=True, slots=True)
class RenderResult:
    output_path: str
    returncode: int
    stderr_tail: str


def execute_ffmpeg(command: list[str], *, runner: ProcessRunner | None = None) -> RenderResult:
    process_runner = runner or ProcessRunner()
    completed = process_runner.run(command)
    output = Path(command[-1])
    if completed.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        raise RenderError(completed.stderr[-4000:] or "FFmpeg gagal tanpa pesan error")
    return RenderResult(str(output), completed.returncode, completed.stderr[-2000:])
