from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TIME_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


@dataclass(frozen=True, slots=True)
class SubtitleCue:
    index: int
    start_seconds: float
    end_seconds: float
    text: str


def _time_to_seconds(value: str) -> float:
    match = _TIME_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Timestamp SRT tidak valid: {value}")
    h, m, s, ms = map(int, match.groups())
    return h * 3600 + m * 60 + s + ms / 1000


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
                start_seconds=_time_to_seconds(start_raw),
                end_seconds=_time_to_seconds(end_raw),
                text="\\N".join(line.strip() for line in lines[2:] if line.strip()),
            )
        )
    return tuple(cues)
