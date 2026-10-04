from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

_TIME_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


@dataclass(frozen=True, slots=True)
class SubtitleCue:
    index: int
    start_seconds: float
    end_seconds: float
    text: str


def parse_srt_timestamp(value: str) -> float:
    match = _TIME_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Timestamp SRT tidak valid: {value}")
    h, m, s, ms = map(int, match.groups())
    if m >= 60 or s >= 60:
        raise ValueError(f"Timestamp SRT tidak valid: {value}")
    return h * 3600 + m * 60 + s + ms / 1000


def format_srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("Timestamp SRT tidak boleh negatif")
    total_ms = int(round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _validate_cue(cue: SubtitleCue) -> None:
    if cue.start_seconds < 0:
        raise ValueError("Waktu mulai cue tidak boleh negatif")
    if cue.end_seconds <= cue.start_seconds:
        raise ValueError("Waktu selesai cue harus lebih besar dari waktu mulai")
    if not cue.text.replace("\\N", "\n").strip():
        raise ValueError("Teks cue tidak boleh kosong")


def parse_srt(path: str | Path) -> tuple[SubtitleCue, ...]:
    text = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    cues: list[SubtitleCue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        index = int(lines[0].strip())
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->", 1)]
        cues.append(
            SubtitleCue(
                index=index,
                start_seconds=parse_srt_timestamp(start_raw),
                end_seconds=parse_srt_timestamp(end_raw),
                text="\\N".join(line.strip() for line in lines[2:] if line.strip()),
            )
        )
    return tuple(cues)


def replace_subtitle_cue(
    cues: tuple[SubtitleCue, ...],
    row: int,
    *,
    text: str,
    start_seconds: float,
    end_seconds: float,
) -> tuple[SubtitleCue, ...]:
    if row < 0 or row >= len(cues):
        raise ValueError("Cue subtitle yang dipilih tidak valid")
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    replacement = replace(
        cues[row],
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        text="\\N".join(line.strip() for line in normalized_text.splitlines()),
    )
    _validate_cue(replacement)
    items = list(cues)
    items[row] = replacement
    return tuple(items)


def serialize_srt(cues: tuple[SubtitleCue, ...]) -> str:
    blocks: list[str] = []
    for cue in cues:
        _validate_cue(cue)
        lines = [
            str(cue.index),
            f"{format_srt_timestamp(cue.start_seconds)} --> {format_srt_timestamp(cue.end_seconds)}",
            *cue.text.replace("\\N", "\n").splitlines(),
        ]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def write_srt_atomic(path: str | Path, cues: tuple[SubtitleCue, ...]) -> Path:
    destination = Path(path).expanduser()
    if destination.suffix.lower() != ".srt":
        raise ValueError("File subtitle hasil edit harus berekstensi .srt")
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = serialize_srt(cues)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
        text=True,
    )
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination.resolve()
