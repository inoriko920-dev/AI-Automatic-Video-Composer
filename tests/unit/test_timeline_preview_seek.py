from aavc.presentation.timeline_preview_seek import timeline_seek_slider_value


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
