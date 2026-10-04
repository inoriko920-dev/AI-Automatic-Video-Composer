from aavc.presentation.subtitle_preview import active_subtitle_cue
from aavc.subtitles.srt import SubtitleCue


def _cues() -> tuple[SubtitleCue, ...]:
    return (
        SubtitleCue(index=1, start_seconds=0.5, end_seconds=1.5, text="Pertama"),
        SubtitleCue(index=2, start_seconds=2.0, end_seconds=3.0, text="Kedua\\NBaris"),
    )


def test_active_subtitle_cue_uses_start_inclusive_end_exclusive_boundaries() -> None:
    cues = _cues()

    assert active_subtitle_cue(cues, 0.49) is None
    assert active_subtitle_cue(cues, 0.5) == cues[0]
    assert active_subtitle_cue(cues, 1.499) == cues[0]
    assert active_subtitle_cue(cues, 1.5) is None
    assert active_subtitle_cue(cues, 2.0) == cues[1]
    assert active_subtitle_cue(cues, 3.0) is None


def test_active_subtitle_cue_clamps_negative_time_to_zero() -> None:
    cue = SubtitleCue(index=1, start_seconds=0.0, end_seconds=1.0, text="Mulai")

    assert active_subtitle_cue((cue,), -2.0) == cue


def test_active_subtitle_cue_returns_none_for_empty_input() -> None:
    assert active_subtitle_cue((), 1.0) is None
