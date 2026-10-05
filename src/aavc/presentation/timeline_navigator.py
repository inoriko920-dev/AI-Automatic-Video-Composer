from __future__ import annotations

from typing import Any, Literal

from aavc.domain.project.models import ProjectState
from aavc.presentation.timeline_zoom_scroll import (
    MAX_TIMELINE_ZOOM_PERCENT,
    MIN_TIMELINE_ZOOM_PERCENT,
    TIMELINE_PLAYHEAD_WIDTH_PX,
    TIMELINE_TRACK_SPACING_PX,
    normalize_timeline_zoom_percent,
    timeline_scene_pixel_width,
    timeline_track_pixel_width,
)

TIMELINE_NAVIGATOR_HEIGHT_PX = 30
TIMELINE_NAVIGATOR_MIN_HANDLE_PX = 24
TIMELINE_NAVIGATOR_EDGE_HIT_PX = 7
TimelineNavigatorHitRegion = Literal["outside", "pan", "left", "right"]


def timeline_navigator_viewport_geometry(
    navigator_width: int | float,
    track_width: int | float,
    viewport_width: int | float,
    scroll_value: int | float,
    maximum_scroll: int | float,
    *,
    minimum_handle_px: int = TIMELINE_NAVIGATOR_MIN_HANDLE_PX,
) -> tuple[int, int]:
    """Return viewport-handle x/width inside the compressed overview."""

    nav_width = max(0, int(round(float(navigator_width))))
    if nav_width <= 0:
        return 0, 0

    track = max(0.0, float(track_width))
    viewport = max(0.0, float(viewport_width))
    maximum = max(0.0, float(maximum_scroll))
    if track <= 0.0 or viewport >= track or maximum <= 0.0:
        return 0, nav_width

    raw_width = int(round(nav_width * min(1.0, viewport / track)))
    handle_width = max(1, min(nav_width, max(int(minimum_handle_px), raw_width)))
    travel = max(0, nav_width - handle_width)
    if travel <= 0:
        return 0, handle_width

    ratio = max(0.0, min(1.0, float(scroll_value) / maximum))
    handle_x = int(round(travel * ratio))
    return max(0, min(travel, handle_x)), handle_width


def timeline_navigator_scroll_value(
    handle_x: int | float,
    navigator_width: int | float,
    handle_width: int | float,
    maximum_scroll: int | float,
) -> int:
    """Map overview handle x back to the main horizontal scrollbar."""

    nav_width = max(0.0, float(navigator_width))
    handle = max(0.0, min(nav_width, float(handle_width)))
    maximum = max(0, int(round(float(maximum_scroll))))
    travel = max(0.0, nav_width - handle)
    if travel <= 0.0 or maximum <= 0:
        return 0

    clamped_x = max(0.0, min(travel, float(handle_x)))
    return max(0, min(maximum, int(round(maximum * (clamped_x / travel)))))


def timeline_navigator_scaled_x(
    track_x: int | float,
    track_width: int | float,
    navigator_width: int | float,
) -> int:
    """Scale one main-track pixel into navigator coordinates."""

    track = max(0.0, float(track_width))
    nav = max(0, int(round(float(navigator_width))))
    if track <= 0.0 or nav <= 0:
        return 0
    ratio = max(0.0, min(1.0, float(track_x) / track))
    return max(0, min(nav, int(round(nav * ratio))))


def timeline_navigator_hit_region(
    mouse_x: int | float,
    handle_x: int | float,
    handle_width: int | float,
    *,
    edge_hit_px: int = TIMELINE_NAVIGATOR_EDGE_HIT_PX,
) -> TimelineNavigatorHitRegion:
    """Return whether the pointer targets the handle center or one resize edge."""

    left = float(handle_x)
    width = max(0.0, float(handle_width))
    right = left + width
    pointer = float(mouse_x)
    if pointer < left or pointer > right:
        return "outside"

    radius = max(1.0, float(edge_hit_px))
    left_distance = abs(pointer - left)
    right_distance = abs(pointer - right)
    nearest_distance = min(left_distance, right_distance)
    if nearest_distance <= radius:
        return "left" if left_distance <= right_distance else "right"
    return "pan"


def timeline_navigator_zoom_percent_for_handle_width(
    durations_seconds: tuple[float, ...],
    viewport_width_px: int | float,
    navigator_width_px: int | float,
    desired_handle_width_px: int | float,
) -> int:
    """Return the zoom whose logical overview viewport width best matches a drag."""

    if not durations_seconds:
        return MIN_TIMELINE_ZOOM_PERCENT

    viewport = max(1.0, float(viewport_width_px))
    navigator = max(1.0, float(navigator_width_px))
    desired = max(1.0, min(navigator, float(desired_handle_width_px)))

    best_zoom = MIN_TIMELINE_ZOOM_PERCENT
    best_distance = float("inf")
    for zoom in range(MIN_TIMELINE_ZOOM_PERCENT, MAX_TIMELINE_ZOOM_PERCENT + 1):
        track_width = max(1.0, float(timeline_track_pixel_width(durations_seconds, zoom)))
        logical_handle_width = navigator * min(1.0, viewport / track_width)
        distance = abs(logical_handle_width - desired)
        if distance < best_distance or (
            abs(distance - best_distance) < 1e-9 and zoom > best_zoom
        ):
            best_zoom = zoom
            best_distance = distance
    return normalize_timeline_zoom_percent(best_zoom)


def timeline_navigator_anchor_scroll_value(
    anchor_edge: Literal["left", "right"],
    anchor_navigator_x: int | float,
    navigator_width: int | float,
    handle_width: int | float,
    maximum_scroll: int | float,
) -> int:
    """Return scroll preserving the opposite navigator edge after a zoom change."""

    handle = max(0.0, float(handle_width))
    anchor = float(anchor_navigator_x)
    handle_x = anchor if anchor_edge == "left" else anchor - handle
    return timeline_navigator_scroll_value(
        handle_x,
        navigator_width,
        handle,
        maximum_scroll,
    )


def install_timeline_navigator(root: Any, project: ProjectState) -> bool:
    """Install a compressed project overview with draggable viewport window."""

    from PySide6.QtCore import QEvent, QObject, QRectF, Qt, QTimer
    from PySide6.QtGui import QColor, QPainter, QPen
    from PySide6.QtWidgets import (
        QBoxLayout,
        QListWidget,
        QScrollArea,
        QSlider,
        QSpinBox,
        QWidget,
    )

    scroll = root.findChild(QScrollArea, "TimelineSceneScrollArea")
    track_widget = root.findChild(QWidget, "TimelineSceneTrack")
    zoom_box = root.findChild(QSpinBox, "TimelineZoomPercent")
    if scroll is None or track_widget is None or zoom_box is None or not project.scenes:
        return False

    existing = root.findChild(QWidget, "TimelineMiniNavigator")
    if existing is not None:
        existing.update()
        return True

    timeline = scroll.parentWidget()
    if timeline is None or timeline.layout() is None:
        return False
    root_layout = timeline.layout()
    bar = scroll.horizontalScrollBar()
    viewport = scroll.viewport()
    durations = tuple(max(0.0, float(scene.duration_seconds)) for scene in project.scenes)

    playhead = root.findChild(QWidget, "TimelinePlayhead")
    progress_sliders = root.findChildren(QSlider)
    progress_slider: Any | None = progress_sliders[0] if progress_sliders else None
    scene_list: Any | None = None
    for listing in root.findChildren(QListWidget):
        if listing.count() == len(project.scenes):
            scene_list = listing
            break

    class _TimelineNavigator(QWidget):
        def __init__(self, parent: Any) -> None:
            super().__init__(parent)
            self._drag_mode: TimelineNavigatorHitRegion | None = None
            self._drag_offset: float | None = None
            self._resize_anchor_nav_x: float | None = None
            self._resize_generation = 0
            self.setObjectName("TimelineMiniNavigator")
            self.setFixedHeight(TIMELINE_NAVIGATOR_HEIGHT_PX)
            self.setMinimumWidth(120)
            self.setMouseTracking(True)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.setToolTip(
                "Overview seluruh timeline. Drag tengah window = pan; drag tepi kiri/kanan = zoom; klik area lain = lompat."
            )

        def _handle_geometry(self) -> tuple[int, int]:
            return timeline_navigator_viewport_geometry(
                self.width(),
                track_widget.width(),
                viewport.width(),
                bar.value(),
                bar.maximum(),
            )

        def _activate_manual_override(self) -> None:
            callback = getattr(root, "_aavc_timeline_set_manual_follow_override", None)
            if callable(callback):
                callback(True, announce=True)

        def _set_scroll_from_mouse(self, mouse_x: float) -> None:
            handle_x, handle_width = self._handle_geometry()
            del handle_x
            offset = self._drag_offset
            if offset is None:
                offset = handle_width / 2.0
            desired_x = float(mouse_x) - float(offset)
            bar.setValue(
                timeline_navigator_scroll_value(
                    desired_x,
                    self.width(),
                    handle_width,
                    bar.maximum(),
                )
            )
            self.update()

        def _set_zoom_from_mouse(self, mouse_x: float) -> None:
            mode = self._drag_mode
            anchor = self._resize_anchor_nav_x
            if mode not in {"left", "right"} or anchor is None:
                return

            pointer = max(0.0, min(float(self.width()), float(mouse_x)))
            desired_width = (
                max(1.0, anchor - pointer)
                if mode == "left"
                else max(1.0, pointer - anchor)
            )
            target_zoom = timeline_navigator_zoom_percent_for_handle_width(
                durations,
                viewport.width(),
                self.width(),
                desired_width,
            )
            self._resize_generation += 1
            generation = self._resize_generation
            zoom_box.setValue(target_zoom)

            def restore_anchor() -> None:
                if generation != self._resize_generation:
                    return
                _actual_x, actual_width = timeline_navigator_viewport_geometry(
                    self.width(),
                    track_widget.width(),
                    viewport.width(),
                    0,
                    bar.maximum(),
                )
                anchored_edge: Literal["left", "right"] = (
                    "right" if mode == "left" else "left"
                )
                bar.setValue(
                    timeline_navigator_anchor_scroll_value(
                        anchored_edge,
                        anchor,
                        self.width(),
                        actual_width,
                        bar.maximum(),
                    )
                )
                self.update()

            QTimer.singleShot(0, restore_anchor)

        def _refresh_hover_cursor(self, mouse_x: float) -> None:
            handle_x, handle_width = self._handle_geometry()
            region = timeline_navigator_hit_region(mouse_x, handle_x, handle_width)
            if region in {"left", "right"}:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif region == "pan":
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.PointingHandCursor)

        def paintEvent(self, event: Any) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.fillRect(self.rect(), QColor("#F8FAFC"))

            nav_width = max(1, self.width())
            track_width = max(1, track_widget.width())
            active_zoom = normalize_timeline_zoom_percent(zoom_box.value())
            scene_top = 7
            scene_height = max(8, self.height() - 14)
            main_x = 0.0
            last_index = len(durations) - 1
            for index, duration in enumerate(durations):
                scene_width = float(timeline_scene_pixel_width(duration, active_zoom))
                left = timeline_navigator_scaled_x(main_x, track_width, nav_width)
                right = timeline_navigator_scaled_x(
                    main_x + scene_width,
                    track_width,
                    nav_width,
                )
                width = max(1, right - left)
                painter.fillRect(
                    left,
                    scene_top,
                    width,
                    scene_height,
                    QColor("#E2E8F0"),
                )
                painter.setPen(QPen(QColor("#CBD5E1"), 1))
                painter.drawRect(left, scene_top, width, scene_height)
                main_x += scene_width
                if index < last_index:
                    main_x += TIMELINE_TRACK_SPACING_PX

            handle_x, handle_width = self._handle_geometry()
            painter.fillRect(
                handle_x,
                2,
                handle_width,
                max(1, self.height() - 4),
                QColor(37, 99, 235, 42),
            )
            painter.setPen(QPen(QColor("#2563EB"), 2))
            painter.drawRoundedRect(
                QRectF(
                    float(handle_x + 1),
                    2.0,
                    float(max(1, handle_width - 2)),
                    float(max(1, self.height() - 5)),
                ),
                4.0,
                4.0,
            )
            painter.setPen(QPen(QColor("#1D4ED8"), 2))
            edge_top = 8
            edge_bottom = max(edge_top + 1, self.height() - 8)
            painter.drawLine(handle_x + 4, edge_top, handle_x + 4, edge_bottom)
            painter.drawLine(
                handle_x + max(4, handle_width - 4),
                edge_top,
                handle_x + max(4, handle_width - 4),
                edge_bottom,
            )

            if playhead is not None and playhead.isVisible():
                playhead_center = (
                    float(playhead.x()) + TIMELINE_PLAYHEAD_WIDTH_PX / 2.0
                )
                playhead_x = timeline_navigator_scaled_x(
                    playhead_center,
                    track_width,
                    nav_width,
                )
                painter.setPen(QPen(QColor("#1D4ED8"), 2))
                painter.drawLine(playhead_x, 1, playhead_x, self.height() - 1)
            painter.end()

        def mousePressEvent(self, event: Any) -> None:  # noqa: N802
            if event.button() != Qt.MouseButton.LeftButton:
                super().mousePressEvent(event)
                return
            handle_x, handle_width = self._handle_geometry()
            mouse_x = float(event.position().x())
            region = timeline_navigator_hit_region(mouse_x, handle_x, handle_width)
            self._activate_manual_override()

            if region == "left":
                self._drag_mode = "left"
                self._resize_anchor_nav_x = float(handle_x + handle_width)
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif region == "right":
                self._drag_mode = "right"
                self._resize_anchor_nav_x = float(handle_x)
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self._drag_mode = "pan"
                if region == "pan":
                    self._drag_offset = mouse_x - handle_x
                else:
                    self._drag_offset = handle_width / 2.0
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self._set_scroll_from_mouse(mouse_x)
            event.accept()

        def mouseMoveEvent(self, event: Any) -> None:  # noqa: N802
            mouse_x = float(event.position().x())
            if self._drag_mode is None:
                self._refresh_hover_cursor(mouse_x)
                super().mouseMoveEvent(event)
                return
            if not bool(event.buttons() & Qt.MouseButton.LeftButton):
                self._drag_mode = None
                self._drag_offset = None
                self._resize_anchor_nav_x = None
                self._refresh_hover_cursor(mouse_x)
                super().mouseMoveEvent(event)
                return

            if self._drag_mode in {"left", "right"}:
                self._set_zoom_from_mouse(mouse_x)
            else:
                self._set_scroll_from_mouse(mouse_x)
            event.accept()

        def mouseReleaseEvent(self, event: Any) -> None:  # noqa: N802
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_mode = None
                self._drag_offset = None
                self._resize_anchor_nav_x = None
                self._refresh_hover_cursor(float(event.position().x()))
                event.accept()
                return
            super().mouseReleaseEvent(event)

    navigator = _TimelineNavigator(timeline)

    insertion_index = root_layout.count()
    for index in range(root_layout.count()):
        child_layout = root_layout.itemAt(index).layout()
        if child_layout is not None and child_layout.indexOf(scroll) >= 0:
            insertion_index = index + 1
            break
    if isinstance(root_layout, QBoxLayout):
        root_layout.insertWidget(insertion_index, navigator)
    else:
        root_layout.addWidget(navigator)

    class _NavigatorResizeFilter(QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:  # noqa: N802
            del watched
            if event.type() == QEvent.Type.Resize:
                QTimer.singleShot(0, navigator.update)
            return False

    resize_filter = _NavigatorResizeFilter(root)
    for target in (viewport, track_widget):
        target.installEventFilter(resize_filter)

    bar.valueChanged.connect(lambda _value: navigator.update())
    bar.rangeChanged.connect(lambda _minimum, _maximum: navigator.update())
    zoom_box.valueChanged.connect(lambda _value: QTimer.singleShot(0, navigator.update))
    if progress_slider is not None:
        progress_slider.valueChanged.connect(
            lambda _value: QTimer.singleShot(0, navigator.update)
        )
    if scene_list is not None:
        scene_list.currentRowChanged.connect(
            lambda _row: QTimer.singleShot(0, navigator.update)
        )

    root._aavc_timeline_navigator = navigator
    root._aavc_timeline_navigator_resize_filter = resize_filter
    root._aavc_timeline_navigator_resize_targets = (viewport, track_widget)
    QTimer.singleShot(0, navigator.update)
    return True
