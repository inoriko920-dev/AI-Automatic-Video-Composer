from __future__ import annotations

from dataclasses import replace

from .srt import SubtitleCue


def stretch_subtitle_cues_from_row(
    cues: tuple[SubtitleCue, ...],
    row: int,
    factor: float,
) -> tuple[SubtitleCue, ...]:
    """Scale timing from one cue onward relative to that cue's start time."""

    if row < 0 or row >= len(cues):
        raise ValueError("Cue subtitle yang dipilih tidak valid")

    scale = float(factor)
    if scale <= 0:
        raise ValueError("Faktor stretch subtitle harus lebih besar dari 0")
    if scale == 1.0:
        return cues

    anchor = cues[row].start_seconds
    result: list[SubtitleCue] = []
    for index, cue in enumerate(cues):
        if index < row:
            result.append(cue)
            continue
        start_seconds = anchor + (cue.start_seconds - anchor) * scale
        end_seconds = anchor + (cue.end_seconds - anchor) * scale
        if start_seconds < 0:
            raise ValueError("Stretch membuat waktu mulai subtitle menjadi negatif")
        result.append(
            replace(
                cue,
                start_seconds=start_seconds,
                end_seconds=end_seconds,
            )
        )
    return tuple(result)
