from pathlib import Path

import pytest

from aavc.subtitles import (
    SubtitleCue,
    format_srt_timestamp,
    parse_srt,
    parse_srt_timestamp,
    replace_subtitle_cue,
    serialize_srt,
    write_srt_atomic,
)


def _sample_cues() -> tuple[SubtitleCue, ...]:
    return (
        SubtitleCue(1, 0.125, 1.5, "Baris satu\\NBaris dua"),
        SubtitleCue(2, 2.0, 3.875, "Cue kedua"),
    )


def test_timestamp_round_trip_and_validation() -> None:
    assert format_srt_timestamp(3661.007) == "01:01:01,007"
    assert parse_srt_timestamp("01:01:01,007") == pytest.approx(3661.007)
    assert parse_srt_timestamp("00:00:01.250") == pytest.approx(1.25)

    with pytest.raises(ValueError, match="Timestamp SRT tidak valid"):
        parse_srt_timestamp("00:61:00,000")
    with pytest.raises(ValueError, match="tidak boleh negatif"):
        format_srt_timestamp(-0.001)


def test_replace_cue_preserves_index_and_other_cues() -> None:
    cues = _sample_cues()
    edited = replace_subtitle_cue(
        cues,
        0,
        text="Teks baru\nbaris kedua",
        start_seconds=0.25,
        end_seconds=1.75,
    )

    assert edited[0] == SubtitleCue(1, 0.25, 1.75, "Teks baru\\Nbaris kedua")
    assert edited[1] is cues[1]

    with pytest.raises(ValueError, match="Teks cue tidak boleh kosong"):
        replace_subtitle_cue(cues, 0, text="  ", start_seconds=0.0, end_seconds=1.0)
    with pytest.raises(ValueError, match="lebih besar"):
        replace_subtitle_cue(cues, 0, text="Valid", start_seconds=1.0, end_seconds=1.0)
    with pytest.raises(ValueError, match="dipilih tidak valid"):
        replace_subtitle_cue(cues, 99, text="Valid", start_seconds=0.0, end_seconds=1.0)


def test_serialize_and_atomic_write_round_trip(tmp_path: Path) -> None:
    cues = _sample_cues()
    serialized = serialize_srt(cues)
    assert "00:00:00,125 --> 00:00:01,500" in serialized
    assert "Baris satu\nBaris dua" in serialized

    destination = tmp_path / "edited.srt"
    resolved = write_srt_atomic(destination, cues)

    assert resolved == destination.resolve()
    assert parse_srt(destination) == cues
    assert not list(tmp_path.glob("*.tmp"))


def test_writing_copy_does_not_touch_original(tmp_path: Path) -> None:
    original = tmp_path / "original.srt"
    original.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nAsli\n",
        encoding="utf-8",
    )
    before = original.read_bytes()
    cues = parse_srt(original)
    edited = replace_subtitle_cue(
        cues,
        0,
        text="Hasil edit",
        start_seconds=0.1,
        end_seconds=1.2,
    )

    copy = tmp_path / "original.edited.srt"
    write_srt_atomic(copy, edited)

    assert original.read_bytes() == before
    assert parse_srt(copy)[0].text == "Hasil edit"


def test_atomic_writer_requires_srt_extension(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="berekstensi .srt"):
        write_srt_atomic(tmp_path / "edited.txt", _sample_cues())
