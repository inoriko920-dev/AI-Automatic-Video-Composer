import pytest

from aavc.presentation.timeline_preview_seek import (
    timeline_drag_target_index,
    timeline_resize_handle_hit,
    timeline_resized_duration,
    timeline_seek_slider_value,
)


def test_timeline_seek_slider_value_maps_horizontal_position() -> None:
    assert timeline_seek_slider_value(0.0, 200.0, 1000) == 0
    assert timeline_seek_slider_value(50.0, 200.0, 1000) == 250
    assert timeline_seek_slider_value(100.0, 200.0, 1000) == 500
    assert timeline_seek_slider_value(200.0, 200.0, 1000) == 1000


def test_timeline_seek_slider_value_clamps_outside_block() -> None:
    assert timeline_seek_slider_value(-20.0, 200.0, 1000) == 0
    assert timeline_seek_slider_value(240.0, 200.0, 1000) == 1000


def test_timeline_seek_slider_value_handles_invalid_width_and_maximum() -> None:
    assert timeline_seek_slider_value(20.0, 0.0, 1000) == 0
    assert timeline_seek_slider_value(20.0, -5.0, 1000) == 0
    assert timeline_seek_slider_value(50.0, 100.0, 0) == 0


def test_timeline_drag_target_index_uses_nearest_scene_center() -> None:
    centers = (100.0, 250.0, 475.0, 800.0)

    assert timeline_drag_target_index(110.0, centers) == 0
    assert timeline_drag_target_index(300.0, centers) == 1
    assert timeline_drag_target_index(520.0, centers) == 2
    assert timeline_drag_target_index(900.0, centers) == 3


def test_timeline_drag_target_index_clamps_by_nearest_edge_and_handles_empty() -> None:
    centers = (100.0, 250.0, 475.0)

    assert timeline_drag_target_index(-500.0, centers) == 0
    assert timeline_drag_target_index(5000.0, centers) == 2
    assert timeline_drag_target_index(10.0, ()) == -1


def test_timeline_resize_handle_hit_only_accepts_right_edge() -> None:
    assert timeline_resize_handle_hit(95.0, 100.0)
    assert timeline_resize_handle_hit(100.0, 100.0)
    assert not timeline_resize_handle_hit(89.0, 100.0)
    assert not timeline_resize_handle_hit(101.0, 100.0)
    assert not timeline_resize_handle_hit(0.0, 0.0)


def test_timeline_resized_duration_scales_from_pixel_delta() -> None:
    assert timeline_resized_duration(4.0, 200.0, 100.0) == 6.0
    assert timeline_resized_duration(4.0, 200.0, -50.0) == 3.0
    assert timeline_resized_duration(4.0, 200.0, 0.0) == 4.0


def test_timeline_resized_duration_clamps_to_positive_minimum() -> None:
    assert timeline_resized_duration(4.0, 200.0, -10000.0) == 0.001
    assert timeline_resized_duration(4.0, 0.0, 100.0) == 4.0

    with pytest.raises(ValueError, match="lebih dari 0"):
        timeline_resized_duration(0.0, 200.0, 10.0)
