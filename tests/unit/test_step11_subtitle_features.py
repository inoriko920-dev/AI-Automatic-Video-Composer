from pathlib import Path

from aavc.domain.project.models import SubtitleAnimationSettings, SubtitleStyle
from aavc.subtitles import compile_srt_to_ass, distribute_words

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def test_subtitle_style_and_animation_are_compiled(tmp_path: Path) -> None:
    out = tmp_path / "styled.ass"
    compile_srt_to_ass(
        FIXTURE / "subtitle.srt",
        out,
        style=SubtitleStyle(font_family="Arial", font_size=60, outline_width=4.0),
        animation=SubtitleAnimationSettings(
            preset="Clean Documentary",
            enter_duration_ms=300,
            exit_duration_ms=300,
        ),
    )
    text = out.read_text(encoding="utf-8")
    assert "Arial,60" in text
    assert r"\fad(300,300)" in text


def test_word_distribution_is_explicit_fallback() -> None:
    timings = distribute_words("satu dua tiga", 1.0, 4.0)
    assert [item.word for item in timings] == ["satu", "dua", "tiga"]
    assert timings[0].start_seconds == 1.0
    assert timings[-1].end_seconds == 4.0
