from aavc.presentation.timeline_zoom_scroll import (
    MAX_TIMELINE_ZOOM_PERCENT,
    MIN_TIMELINE_SCENE_WIDTH_PX,
    MIN_TIMELINE_ZOOM_PERCENT,
    normalize_timeline_zoom_percent,
    timeline_scene_pixel_width,
    timeline_track_pixel_width,
)


def test_timeline_zoom_percent_clamps_to_supported_range() -> None:
    assert normalize_timeline_zoom_percent(10) == MIN_TIMELINE_ZOOM_PERCENT
    assert normalize_timeline_zoom_percent(100) == 100
    assert normalize_timeline_zoom_percent(999) == MAX_TIMELINE_ZOOM_PERCENT


def test_timeline_scene_width_scales_with_zoom_and_duration() -> None:
    assert timeline_scene_pixel_width(4.0, 200) == 2 * timeline_scene_pixel_width(4.0, 100)
    assert timeline_scene_pixel_width(8.0, 100) == 2 * timeline_scene_pixel_width(4.0, 100)
    assert timeline_scene_pixel_width(0.001, 100) == MIN_TIMELINE_SCENE_WIDTH_PX


def test_timeline_track_width_adds_scene_widths_and_spacing() -> None:
    first = timeline_scene_pixel_width(2.0, 100)
    second = timeline_scene_pixel_width(3.0, 100)

    assert timeline_track_pixel_width((2.0, 3.0), 100) == first + second + 3
    assert timeline_track_pixel_width((), 100) == 0
