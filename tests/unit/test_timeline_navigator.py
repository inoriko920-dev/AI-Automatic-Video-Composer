from __future__ import annotations

from aavc.presentation.timeline_navigator import (
    timeline_navigator_scaled_x,
    timeline_navigator_scroll_value,
    timeline_navigator_viewport_geometry,
)


def test_full_track_view_uses_full_navigator_handle() -> None:
    assert timeline_navigator_viewport_geometry(240, 800, 800, 0, 0) == (0, 240)
    assert timeline_navigator_viewport_geometry(240, 0, 800, 0, 0) == (0, 240)


def test_viewport_geometry_tracks_scroll_ratio() -> None:
    assert timeline_navigator_viewport_geometry(
        200,
        1000,
        250,
        375,
        750,
    ) == (75, 50)


def test_very_long_track_keeps_minimum_draggable_handle() -> None:
    assert timeline_navigator_viewport_geometry(
        100,
        10000,
        500,
        4750,
        9500,
    ) == (38, 24)


def test_drag_handle_maps_back_to_main_scrollbar() -> None:
    assert timeline_navigator_scroll_value(75, 200, 50, 750) == 375
    assert timeline_navigator_scroll_value(0, 200, 50, 750) == 0
    assert timeline_navigator_scroll_value(150, 200, 50, 750) == 750


def test_drag_mapping_clamps_beyond_overview_edges() -> None:
    assert timeline_navigator_scroll_value(-100, 200, 50, 750) == 0
    assert timeline_navigator_scroll_value(500, 200, 50, 750) == 750
    assert timeline_navigator_scroll_value(10, 20, 20, 100) == 0


def test_track_pixel_scaling_clamps_to_navigator() -> None:
    assert timeline_navigator_scaled_x(500, 1000, 200) == 100
    assert timeline_navigator_scaled_x(-50, 1000, 200) == 0
    assert timeline_navigator_scaled_x(1500, 1000, 200) == 200
    assert timeline_navigator_scaled_x(20, 0, 200) == 0
