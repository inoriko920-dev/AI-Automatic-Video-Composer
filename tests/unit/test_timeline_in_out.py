from __future__ import annotations

import pytest

from aavc.presentation.timeline_in_out import (
    timeline_in_out_duration_seconds,
    timeline_set_in_out_point,
)
from aavc.presentation.timeline_markers import timeline_marker_seek_target


def test_set_in_point_snaps_to_project_frame() -> None:
    in_point, out_point = timeline_set_in_out_point(
        None,
        None,
        "in",
        1.016,
        10.0,
        30,
    )

    assert in_point == 1.0
    assert out_point is None


def test_setting_opposite_point_normalizes_range_order() -> None:
    in_point, out_point = timeline_set_in_out_point(
        None,
        2.0,
        "in",
        4.0,
        10.0,
        30,
    )

    assert in_point == 2.0
    assert out_point == 4.0


def test_setting_out_before_existing_in_normalizes_range_order() -> None:
    in_point, out_point = timeline_set_in_out_point(
        6.0,
        None,
        "out",
        3.0,
        10.0,
        30,
    )

    assert in_point == 3.0
    assert out_point == 6.0


def test_equal_in_and_out_never_leave_zero_length_range() -> None:
    in_point, out_point = timeline_set_in_out_point(
        3.0,
        None,
        "out",
        3.0,
        10.0,
        30,
    )

    assert in_point is None
    assert out_point == 3.0


def test_in_out_duration_requires_complete_range() -> None:
    assert timeline_in_out_duration_seconds(None, 4.0) == 0.0
    assert timeline_in_out_duration_seconds(2.25, None) == 0.0
    assert timeline_in_out_duration_seconds(2.25, 5.75) == pytest.approx(3.5)


def test_global_range_endpoint_maps_to_scene_local_position() -> None:
    durations = (2.0, 3.0, 4.0)

    assert timeline_marker_seek_target(durations, 2.0) == (1, 0.0)
    assert timeline_marker_seek_target(durations, 4.5) == (1, 2.5)
    assert timeline_marker_seek_target(durations, 9.0) == (2, 4.0)
