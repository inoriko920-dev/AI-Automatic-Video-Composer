from __future__ import annotations

from aavc.presentation.timeline_magnet_control import (
    normalize_timeline_magnet_enabled,
    set_timeline_magnet_runtime_bypass,
    set_timeline_magnet_runtime_enabled,
    set_timeline_magnet_runtime_target_enabled,
    timeline_magnet_active,
    timeline_magnet_runtime_active,
    timeline_magnet_runtime_target_enabled,
)
from aavc.presentation.timeline_magnetic_edit import timeline_magnetic_split_local_seconds
from aavc.presentation.timeline_magnetic_snap import timeline_magnetic_snap_target
from aavc.presentation.timeline_zoom_scroll import timeline_global_seconds_pixel_x


def teardown_function() -> None:
    set_timeline_magnet_runtime_bypass(False)
    set_timeline_magnet_runtime_enabled(True)
    set_timeline_magnet_runtime_target_enabled("marker", True)
    set_timeline_magnet_runtime_target_enabled("scene", True)
    set_timeline_magnet_runtime_target_enabled("playhead", True)


def test_magnet_state_defaults_on_and_normalizes_common_values() -> None:
    assert normalize_timeline_magnet_enabled(None) is True
    assert normalize_timeline_magnet_enabled(True) is True
    assert normalize_timeline_magnet_enabled(False) is False
    assert normalize_timeline_magnet_enabled("on") is True
    assert normalize_timeline_magnet_enabled("OFF") is False
    assert normalize_timeline_magnet_enabled(1) is True
    assert normalize_timeline_magnet_enabled(0) is False


def test_alt_bypass_does_not_change_global_enabled_state() -> None:
    assert timeline_magnet_active(True, alt_bypass=False) is True
    assert timeline_magnet_active(True, alt_bypass=True) is False
    assert timeline_magnet_active(False, alt_bypass=False) is False

    set_timeline_magnet_runtime_enabled(True)
    assert timeline_magnet_runtime_active(alt_bypass=False) is True
    assert timeline_magnet_runtime_active(alt_bypass=True) is False
    assert timeline_magnet_runtime_active(alt_bypass=False) is True


def test_target_runtime_state_is_independent_per_category() -> None:
    assert timeline_magnet_runtime_target_enabled("marker") is True
    assert timeline_magnet_runtime_target_enabled("scene") is True
    assert timeline_magnet_runtime_target_enabled("playhead") is True

    set_timeline_magnet_runtime_target_enabled("marker", False)
    assert timeline_magnet_runtime_target_enabled("marker") is False
    assert timeline_magnet_runtime_target_enabled("scene") is True
    assert timeline_magnet_runtime_target_enabled("playhead") is True


def test_transient_runtime_bypass_suppresses_magnetic_target() -> None:
    durations = (5.0, 5.0)
    marker_seconds = (3.0,)
    marker_x = timeline_global_seconds_pixel_x(durations, 3.0, 100)

    set_timeline_magnet_runtime_enabled(True)
    set_timeline_magnet_runtime_bypass(False)
    assert timeline_magnetic_snap_target(
        durations,
        marker_x,
        100,
        30,
        markers_seconds=marker_seconds,
    ) == (3.0, "marker")

    set_timeline_magnet_runtime_bypass(True)
    assert (
        timeline_magnetic_snap_target(
            durations,
            marker_x,
            100,
            30,
            markers_seconds=marker_seconds,
        )
        is None
    )


def test_snap_target_settings_filter_marker_scene_and_playhead_independently() -> None:
    durations = (5.0, 5.0)

    marker_x = timeline_global_seconds_pixel_x(durations, 3.0, 100)
    assert timeline_magnetic_snap_target(
        durations,
        marker_x,
        100,
        30,
        markers_seconds=(3.0,),
    ) == (3.0, "marker")
    set_timeline_magnet_runtime_target_enabled("marker", False)
    assert (
        timeline_magnetic_snap_target(
            durations,
            marker_x,
            100,
            30,
            markers_seconds=(3.0,),
        )
        is None
    )

    scene_x = timeline_global_seconds_pixel_x(durations, 5.0, 100)
    assert timeline_magnetic_snap_target(durations, scene_x, 100, 30) == (5.0, "scene")
    set_timeline_magnet_runtime_target_enabled("scene", False)
    assert timeline_magnetic_snap_target(durations, scene_x, 100, 30) is None

    playhead_x = timeline_global_seconds_pixel_x(durations, 4.0, 100)
    assert timeline_magnetic_snap_target(
        durations,
        playhead_x,
        100,
        30,
        playhead_seconds=4.0,
    ) == (4.0, "playhead")
    set_timeline_magnet_runtime_target_enabled("playhead", False)
    assert (
        timeline_magnetic_snap_target(
            durations,
            playhead_x,
            100,
            30,
            playhead_seconds=4.0,
        )
        is None
    )


def test_magnet_off_preserves_unsnapped_split_position() -> None:
    durations = (5.0, 5.0)
    local_seconds = 2.95

    set_timeline_magnet_runtime_enabled(True)
    snapped_local, snapped = timeline_magnetic_split_local_seconds(
        durations,
        0,
        local_seconds,
        100,
        30,
        markers_seconds=(3.0,),
    )
    assert snapped is True
    assert snapped_local == 3.0

    set_timeline_magnet_runtime_enabled(False)
    unsnapped_local, unsnapped = timeline_magnetic_split_local_seconds(
        durations,
        0,
        local_seconds,
        100,
        30,
        markers_seconds=(3.0,),
    )
    assert unsnapped is False
    assert unsnapped_local == local_seconds


def test_split_marker_target_setting_disables_marker_and_in_out_anchors() -> None:
    durations = (5.0, 5.0)
    local_seconds = 2.95

    set_timeline_magnet_runtime_target_enabled("marker", False)
    unsnapped_local, snapped = timeline_magnetic_split_local_seconds(
        durations,
        0,
        local_seconds,
        100,
        30,
        markers_seconds=(3.0,),
    )
    assert snapped is False
    assert unsnapped_local == local_seconds
