import pytest

from aavc.presentation.timeline_keyboard_seek import (
    timeline_frame_step_seconds,
    timeline_keyboard_seek_target,
)


def test_frame_step_uses_project_fps() -> None:
    assert timeline_frame_step_seconds(30) == pytest.approx(1.0 / 30.0)
    assert timeline_frame_step_seconds(60) == pytest.approx(1.0 / 60.0)
    assert timeline_frame_step_seconds(0) == pytest.approx(1.0)


def test_keyboard_seek_moves_within_scene() -> None:
    durations = (2.0, 3.0)

    assert timeline_keyboard_seek_target(durations, 0, 1.0, 1.0 / 30.0) == pytest.approx(
        (0, 1.0 + 1.0 / 30.0)
    )
    assert timeline_keyboard_seek_target(durations, 1, 1.5, -1.0) == pytest.approx(
        (1, 0.5)
    )


def test_keyboard_seek_crosses_scene_boundaries() -> None:
    durations = (2.0, 3.0)

    assert timeline_keyboard_seek_target(durations, 0, 1.99, 0.02) == pytest.approx(
        (1, 0.01)
    )
    assert timeline_keyboard_seek_target(durations, 1, 0.01, -0.02) == pytest.approx(
        (0, 1.99)
    )
    assert timeline_keyboard_seek_target(durations, 0, 1.0, 1.0) == (1, 0.0)


def test_keyboard_seek_clamps_to_project_edges() -> None:
    durations = (2.0, 3.0)

    assert timeline_keyboard_seek_target(durations, 0, 0.1, -10.0) == (0, 0.0)
    assert timeline_keyboard_seek_target(durations, 1, 2.9, 10.0) == (1, 3.0)


def test_keyboard_seek_handles_empty_and_out_of_range_scene_index() -> None:
    assert timeline_keyboard_seek_target((), 0, 0.0, 1.0) is None
    assert timeline_keyboard_seek_target((2.0, 3.0), 99, 1.0, 0.0) == (1, 1.0)
    assert timeline_keyboard_seek_target((2.0, 3.0), -99, 1.0, 0.0) == (0, 1.0)
