from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from uuid import uuid4

from aavc.domain.errors import RenderError
from aavc.platform.process_runner import (
    WINDOWS_COMMAND_LINE_LIMIT,
    ProcessRunner,
    windows_command_line_units,
)


@dataclass(frozen=True, slots=True)
class RenderResult:
    output_path: str
    returncode: int
    stderr_tail: str


def _temporary_output_path(output: Path) -> Path:
    return output.with_name(
        f".{output.stem}.aavc-render-{uuid4().hex}{output.suffix}"
    )


def ensure_windows_command_line_fits(
    argv: list[str],
    *,
    is_windows: bool | None = None,
) -> None:
    target_is_windows = os.name == "nt" if is_windows is None else is_windows
    if not target_is_windows:
        return
    units = windows_command_line_units(argv)
    if units > WINDOWS_COMMAND_LINE_LIMIT:
        raise RenderError(
            "Perintah FFmpeg terlalu panjang untuk Windows "
            f"({units} > {WINDOWS_COMMAND_LINE_LIMIT} UTF-16 units). "
            "Pendekkan lokasi file input/output atau pindahkan aset ke folder "
            "dengan path lebih pendek."
        )


def execute_ffmpeg(command: list[str], *, runner: ProcessRunner | None = None) -> RenderResult:
    if not command:
        raise RenderError("Perintah FFmpeg kosong")

    process_runner = runner or ProcessRunner()
    output = Path(command[-1])
    temporary = _temporary_output_path(output)
    render_command = [*command[:-1], str(temporary)]
    ensure_windows_command_line_fits(render_command)

    try:
        completed = process_runner.run(render_command)
        if (
            completed.returncode != 0
            or not temporary.exists()
            or temporary.stat().st_size == 0
        ):
            raise RenderError(completed.stderr[-4000:] or "FFmpeg gagal tanpa pesan error")

        try:
            temporary.replace(output)
        except OSError as error:
            raise RenderError(f"Gagal menyelesaikan file output render: {error}") from error

        return RenderResult(str(output), completed.returncode, completed.stderr[-2000:])
    finally:
        temporary.unlink(missing_ok=True)
