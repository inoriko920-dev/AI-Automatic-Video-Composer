from __future__ import annotations

from typing import Any

from aavc.domain.project.models import ProjectState

MIN_TIMELINE_ZOOM_PERCENT = 50
MAX_TIMELINE_ZOOM_PERCENT = 400
DEFAULT_TIMELINE_ZOOM_PERCENT = 100
TIMELINE_PIXELS_PER_SECOND = 48.0
MIN_TIMELINE_SCENE_WIDTH_PX = 56
MAX_TIMELINE_SCENE_WIDTH_PX = 20000
TIMELINE_TRACK_SPACING_PX = 3


def normalize_timeline_zoom_percent(value: int | float) -> int:
    return max(
        MIN_TIMELINE_ZOOM_PERCENT,
        min(MAX_TIMELINE_ZOOM_PERCENT, int(round(float(value)))),
    )


def timeline_scene_pixel_width(
    duration_seconds: float,
    zoom_percent: int | float,
) -> int:
    zoom = normalize_timeline_zoom_percent(zoom_percent) / 100.0
    width = int(round(max(0.0, float(duration_seconds)) * TIMELINE_PIXELS_PER_SECOND * zoom))
    return max(
        MIN_TIMELINE_SCENE_WIDTH_PX,
        min(MAX_TIMELINE_SCENE_WIDTH_PX, width),
    )


def timeline_track_pixel_width(
    durations_seconds: tuple[float, ...],
    zoom_percent: int | float,
) -> int:
    if not durations_seconds:
        return 0
    return sum(
        timeline_scene_pixel_width(duration, zoom_percent)
        for duration in durations_seconds
    ) + TIMELINE_TRACK_SPACING_PX * (len(durations_seconds) - 1)


def _stored_int_property(owner: Any, name: str, default: int) -> int:
    value = owner.property(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def install_timeline_zoom_scroll(root: Any, project: ProjectState) -> bool:
    """Wrap the Scene track in horizontal scroll and add persistent UI-only zoom."""

    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QWidget,
    )

    labels = root.findChildren(QLabel)
    title = next(
        (label for label in labels if label.text().startswith("Timeline Scene ·")),
        None,
    )
    if title is None:
        return False

    timeline = title.parentWidget()
    if timeline is None or timeline.layout() is None:
        return False
    root_layout = timeline.layout()

    track_layout: Any | None = None
    for index in range(root_layout.count()):
        candidate = root_layout.itemAt(index).layout()
        if candidate is None:
            continue
        for item_index in range(candidate.count()):
            widget = candidate.itemAt(item_index).widget()
            if isinstance(widget, QLabel) and widget.text() == "V1  Scene":
                track_layout = candidate
                break
        if track_layout is not None:
            break
    if track_layout is None:
        return False

    buttons: list[Any] = []
    for scene in project.scenes:
        prefix = f"Sc{scene.scene_number:02d}\n"
        button = next(
            (
                candidate
                for candidate in root.findChildren(QPushButton)
                if candidate.text().startswith(prefix)
            ),
            None,
        )
        if button is None:
            return False
        buttons.append(button)

    owner = timeline.window()
    zoom_percent = normalize_timeline_zoom_percent(
        _stored_int_property(
            owner,
            "aavcTimelineZoomPercent",
            DEFAULT_TIMELINE_ZOOM_PERCENT,
        )
    )
    saved_scroll = max(0, _stored_int_property(owner, "aavcTimelineScrollValue", 0))

    for button in buttons:
        track_layout.removeWidget(button)

    scroll = QScrollArea(timeline)
    scroll.setObjectName("TimelineSceneScrollArea")
    scroll.setWidgetResizable(False)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    track_widget = QWidget(scroll)
    track_widget.setObjectName("TimelineSceneTrack")
    content_layout = QHBoxLayout(track_widget)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(TIMELINE_TRACK_SPACING_PX)
    for button in buttons:
        content_layout.addWidget(button)
    scroll.setWidget(track_widget)
    track_layout.addWidget(scroll, 1)

    durations = tuple(scene.duration_seconds for scene in project.scenes)

    def apply_zoom(value: int) -> None:
        normalized = normalize_timeline_zoom_percent(value)
        owner.setProperty("aavcTimelineZoomPercent", normalized)
        current_scroll = scroll.horizontalScrollBar().value()
        for button, scene in zip(buttons, project.scenes, strict=True):
            button.setFixedWidth(
                timeline_scene_pixel_width(scene.duration_seconds, normalized)
            )
        track_widget.setFixedWidth(timeline_track_pixel_width(durations, normalized))
        track_widget.adjustSize()
        QTimer.singleShot(
            0,
            lambda: scroll.horizontalScrollBar().setValue(
                min(current_scroll, scroll.horizontalScrollBar().maximum())
            ),
        )

    apply_zoom(zoom_percent)

    header_layout = root_layout.itemAt(0).layout() if root_layout.count() else None
    if header_layout is not None:
        snap_label = QLabel("Snap 0,1 dtk", timeline)
        snap_label.setStyleSheet("color:#64748B; font-size:9px;")
        header_layout.addWidget(snap_label)
        header_layout.addWidget(QLabel("Zoom", timeline))
        zoom_box = QSpinBox(timeline)
        zoom_box.setObjectName("TimelineZoomPercent")
        zoom_box.setRange(MIN_TIMELINE_ZOOM_PERCENT, MAX_TIMELINE_ZOOM_PERCENT)
        zoom_box.setSingleStep(25)
        zoom_box.setSuffix("%")
        zoom_box.setValue(zoom_percent)
        zoom_box.setToolTip("Zoom visual timeline. Tidak mengubah durasi atau file project.")
        zoom_box.valueChanged.connect(apply_zoom)
        header_layout.addWidget(zoom_box)

    bar = scroll.horizontalScrollBar()
    bar.valueChanged.connect(
        lambda value: owner.setProperty("aavcTimelineScrollValue", int(value))
    )

    def restore_scroll() -> None:
        bar.setValue(min(saved_scroll, bar.maximum()))

    QTimer.singleShot(0, restore_scroll)

    for label in labels:
        if label.text().startswith("Lebar blok mengikuti durasi scene."):
            label.setText(
                f"{label.text()} Resize timeline snap 0,1 detik. Zoom {zoom_percent}%; "
                "gunakan scrollbar untuk navigasi horizontal."
            )
            break
    return True
