from __future__ import annotations

from dataclasses import replace

from .srt import SubtitleCue


def shift_subtitle_cues(
    cues: tuple[SubtitleCue, ...],
    offset_seconds: float,
) -> tuple[SubtitleCue, ...]:
    """Shift every cue by one offset while preserving text, index, and duration."""

    offset = float(offset_seconds)
    if offset == 0.0 or not cues:
        return cues

    earliest_start = min(cue.start_seconds for cue in cues)
    if earliest_start + offset < 0:
        raise ValueError("Offset membuat waktu mulai subtitle menjadi negatif")

    return tuple(
        replace(
            cue,
            start_seconds=cue.start_seconds + offset,
            end_seconds=cue.end_seconds + offset,
        )
        for cue in cues
    )
