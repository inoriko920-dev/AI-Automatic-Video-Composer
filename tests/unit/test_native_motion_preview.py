import pytest

from aavc.domain.project.models import AnimationAssignment
from aavc.presentation.motion_preview import native_motion_preview_offset


def _assignment(
    enter: str = "Rise",
    exit_effect: str = "Drift",
    *,
    intensity: float = 1.0,
) -> AnimationAssignment:
    return AnimationAssignment(
        scene_number=1,
        asset_id="A001",
        enter_effect=enter,
        exit_effect=exit_effect,
        intensity=intensity,
    )


def test_preview_offset_is_zero_without_assignment() -> None:
    assert native_motion_preview_offset(
        None,
        time_seconds=0.0,
        duration_seconds=2.0,
    ).x == 0.0
    assert native_motion_preview_offset(
        None,
        time_seconds=0.0,
        duration_seconds=2.0,
    ).y == 0.0


def test_rise_enter_matches_phase_one_window() -> None:
    assignment = _assignment("Rise", "Fade")

    start = native_motion_preview_offset(
        assignment,
        time_seconds=0.0,
        duration_seconds=2.0,
    )
    halfway = native_motion_preview_offset(
        assignment,
        time_seconds=0.125,
        duration_seconds=2.0,
    )
    settled = native_motion_preview_offset(
        assignment,
        time_seconds=0.25,
        duration_seconds=2.0,
    )

    assert start.y == pytest.approx(0.08)
    assert halfway.y == pytest.approx(0.04)
    assert settled.y == pytest.approx(0.0)
    assert start.x == pytest.approx(0.0)


def test_drift_exit_matches_phase_one_window() -> None:
    assignment = _assignment("Fade", "Drift")

    before_exit = native_motion_preview_offset(
        assignment,
        time_seconds=1.75,
        duration_seconds=2.0,
    )
    halfway = native_motion_preview_offset(
        assignment,
        time_seconds=1.875,
        duration_seconds=2.0,
    )
    end = native_motion_preview_offset(
        assignment,
        time_seconds=2.0,
        duration_seconds=2.0,
    )

    assert before_exit.x == pytest.approx(0.0)
    assert halfway.x == pytest.approx(0.03)
    assert end.x == pytest.approx(0.06)
    assert end.y == pytest.approx(0.0)


def test_preview_offset_respects_intensity_and_ignores_non_native_effects() -> None:
    doubled = native_motion_preview_offset(
        _assignment("Rise", "Blur", intensity=2.0),
        time_seconds=0.0,
        duration_seconds=2.0,
    )
    non_native = native_motion_preview_offset(
        _assignment("Fade", "Blur"),
        time_seconds=0.0,
        duration_seconds=2.0,
    )

    assert doubled.y == pytest.approx(0.16)
    assert non_native.x == pytest.approx(0.0)
    assert non_native.y == pytest.approx(0.0)


def test_short_scene_uses_half_duration_window() -> None:
    assignment = _assignment("Pan", "Drift")

    midpoint = native_motion_preview_offset(
        assignment,
        time_seconds=0.05,
        duration_seconds=0.1,
    )

    assert midpoint.x == pytest.approx(0.0)
    assert midpoint.y == pytest.approx(0.0)
