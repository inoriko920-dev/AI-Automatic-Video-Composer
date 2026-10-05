from __future__ import annotations

from typing import Any, Literal

from aavc.domain.project.models import ProjectState
from aavc.presentation.motion_preview import preview_scrub_seconds
from aavc.presentation.timeline_markers import (
    timeline_marker_global_seconds,
    timeline_marker_seek_target,
    timeline_marker_snap_seconds,
)
from aavc.presentation.timeline_ruler_seek import timeline_slider_value_for_local_seconds
from aavc.presentation.timeline_zoom_scroll import (
    DEFAULT_TIMELINE_ZOOM_PERCENT,
    normalize_timeline_zoom_percent,
    timeline_global_seconds_pixel_x,
)

TimelineRangePoint = Literal["in", "out"]
TIMELINE_IN_OUT_EPSILON_SECONDS = 1e-6
TIMELINE_IN_OUT_GLYPH_WIDTH_PX = 12


def timeline_set_in_out_point(
    in_seconds: float | None,
    out_seconds: float | None,
    point: TimelineRangePoint,
    global_seconds: float,
    total_duration_seconds: float,
    fps: int | float,
) -> tuple[float | None, float | None]:
    """Set a frame-snapped In/Out point while keeping a valid ordered range."""

    snapped = timeline_marker_snap_seconds(
        global_seconds,
        total_duration_seconds,
        fps,
    )
    current_in = (
        None
        if in_seconds is None
        else timeline_marker_snap_seconds(in_seconds, total_duration_seconds, fps)
    )
    current_out = (
        None
        if out_seconds is None
        else timeline_marker_snap_seconds(out_seconds, total_duration_seconds, fps)
    )

    if point == "in":
        current_in = snapped
    elif point == "out":
        current_out = snapped
    else:
        raise ValueError(f"Unsupported timeline range point: {point}")

    if current_in is None or current_out is None:
        return current_in, current_out
    if abs(current_in - current_out) <= TIMELINE_IN_OUT_EPSILON_SECONDS:
        if point == "in":
            return current_in, None
        return None, current_out
    if current_in > current_out:
        return current_out, current_in
    return current_in, current_out


def timeline_in_out_duration_seconds(
    in_seconds: float | None,
    out_seconds: float | None,
) -> float:
    """Return the selected range duration, or zero until both points exist."""

    if in_seconds is None or out_seconds is None:
        return 0.0
    return round(max(0.0, float(out_seconds) - float(in_seconds)), 6)


def install_timeline_in_out(root: Any, project: ProjectState) -> bool:
    """Install session-only timeline In/Out points and keyboard navigation."""

    from PySide6.QtCore import QEvent, QObject, Qt
    from PySide6.QtGui import QColor, QPainter, QPen
    from PySide6.QtWidgets import (
        QAbstractSpinBox,
        QApplication,
        QLineEdit,
        QListWidget,
        QPlainTextEdit,
        QSlider,
        QSpinBox,
        QTextEdit,
        QWidget,
    )

    if not project.scenes:
        return False

    ruler = root.findChild(QWidget, "TimelineTimeRuler")
    if ruler is None:
        return False

    scene_list: Any | None = None
    for listing in root.findChildren(QListWidget):
        if listing.count() != len(project.scenes):
            continue
        first = listing.item(0)
        if first is not None and first.text().startswith(
            f"{project.scenes[0].scene_number:02d}. Scene"
        ):
            scene_list = listing
            break

    sliders = root.findChildren(QSlider)
    progress_slider: Any | None = sliders[0] if sliders else None
    app: Any = QApplication.instance()
    if scene_list is None or progress_slider is None or app is None:
        return False

    durations = tuple(scene.duration_seconds for scene in project.scenes)
    total_duration = sum(max(0.0, float(item)) for item in durations)
    owner: Any = ruler.window()
    signature = (project.source_docx, project.asset_directory)
    if getattr(owner, "_aavc_timeline_in_out_project_signature", None) != signature:
        owner._aavc_timeline_in_out_project_signature = signature
        owner._aavc_timeline_in_seconds = None
        owner._aavc_timeline_out_seconds = None
    else:
        if not hasattr(owner, "_aavc_timeline_in_seconds"):
            owner._aavc_timeline_in_seconds = None
        if not hasattr(owner, "_aavc_timeline_out_seconds"):
            owner._aavc_timeline_out_seconds = None

    class _TimelineRangeOverlay(QWidget):
        def __init__(self, parent: Any) -> None:
            super().__init__(parent)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        def paintEvent(self, event: Any) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(37, 99, 235, 38))
            painter.setPen(QPen(QColor("#2563EB"), 1))
            painter.drawLine(0, 0, 0, self.height())
            painter.drawLine(max(0, self.width() - 1), 0, max(0, self.width() - 1), self.height())
            painter.end()

    class _TimelineRangeGlyph(QWidget):
        def __init__(self, parent: Any, label: str) -> None:
            super().__init__(parent)
            self._label = label
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        def paintEvent(self, event: Any) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            color = QColor("#2563EB")
            painter.setPen(QPen(color, 2))
            center_x = self.width() // 2
            painter.drawLine(center_x, 8, center_x, self.height())
            painter.setPen(color)
            painter.drawText(1, 8, self._label)
            painter.end()

    range_widgets: list[Any] = []
    root._aavc_timeline_in_out_widgets = range_widgets

    def range_points() -> tuple[float | None, float | None]:
        raw_in = getattr(owner, "_aavc_timeline_in_seconds", None)
        raw_out = getattr(owner, "_aavc_timeline_out_seconds", None)
        in_point = None if raw_in is None else float(raw_in)
        out_point = None if raw_out is None else float(raw_out)
        return in_point, out_point

    def stored_zoom_percent() -> int:
        value = owner.property("aavcTimelineZoomPercent")
        try:
            raw = DEFAULT_TIMELINE_ZOOM_PERCENT if value is None else int(value)
        except (TypeError, ValueError):
            raw = DEFAULT_TIMELINE_ZOOM_PERCENT
        return normalize_timeline_zoom_percent(raw)

    def clear_range_widgets() -> None:
        for widget in range_widgets:
            widget.deleteLater()
        range_widgets.clear()

    def add_glyph(seconds: float, label: str, zoom: int) -> None:
        x = timeline_global_seconds_pixel_x(durations, seconds, zoom)
        glyph = _TimelineRangeGlyph(ruler, label)
        glyph.setObjectName(f"Timeline{label}Point")
        glyph.setGeometry(
            max(0, x - TIMELINE_IN_OUT_GLYPH_WIDTH_PX // 2),
            0,
            TIMELINE_IN_OUT_GLYPH_WIDTH_PX,
            max(1, ruler.height()),
        )
        glyph.setToolTip(f"{label} point · {seconds:.3f} detik")
        glyph.show()
        glyph.raise_()
        range_widgets.append(glyph)

    def refresh_range_widgets() -> None:
        clear_range_widgets()
        in_point, out_point = range_points()
        zoom = stored_zoom_percent()
        if in_point is not None and out_point is not None:
            in_x = timeline_global_seconds_pixel_x(durations, in_point, zoom)
            out_x = timeline_global_seconds_pixel_x(durations, out_point, zoom)
            left = min(in_x, out_x)
            right = max(in_x, out_x)
            overlay = _TimelineRangeOverlay(ruler)
            overlay.setObjectName("TimelineInOutRange")
            overlay.setGeometry(
                left,
                0,
                max(1, right - left + 1),
                max(1, ruler.height()),
            )
            overlay.setToolTip(
                f"Range In/Out · {in_point:.3f}–{out_point:.3f} detik · "
                f"durasi {timeline_in_out_duration_seconds(in_point, out_point):.3f} detik"
            )
            overlay.show()
            overlay.raise_()
            range_widgets.append(overlay)
        if in_point is not None:
            add_glyph(in_point, "I", zoom)
        if out_point is not None:
            add_glyph(out_point, "O", zoom)

    def show_status(message: str) -> None:
        status_bar = owner.statusBar() if hasattr(owner, "statusBar") else None
        if status_bar is not None:
            status_bar.showMessage(message, 6000)

    def current_global_seconds() -> float:
        row = int(scene_list.currentRow())
        if row < 0 or row >= len(durations):
            return 0.0
        local = preview_scrub_seconds(
            progress_slider.value(),
            progress_slider.maximum(),
            durations[row],
        )
        return timeline_marker_global_seconds(durations, row, local)

    def seek_global(global_seconds: float) -> None:
        target = timeline_marker_seek_target(durations, global_seconds)
        if target is None:
            return
        scene_index, local_seconds = target
        if scene_list.currentRow() != scene_index:
            scene_list.setCurrentRow(scene_index)
        slider_value = timeline_slider_value_for_local_seconds(
            local_seconds,
            durations[scene_index],
            progress_slider.maximum(),
        )
        progress_slider.setValue(slider_value)
        progress_slider.sliderMoved.emit(slider_value)
        progress_slider.sliderReleased.emit()

    def set_point(point: TimelineRangePoint) -> None:
        in_point, out_point = range_points()
        updated_in, updated_out = timeline_set_in_out_point(
            in_point,
            out_point,
            point,
            current_global_seconds(),
            total_duration,
            project.fps,
        )
        owner._aavc_timeline_in_seconds = updated_in
        owner._aavc_timeline_out_seconds = updated_out
        refresh_range_widgets()
        point_label = "In" if point == "in" else "Out"
        chosen = updated_in if point == "in" else updated_out
        if chosen is None:
            chosen = updated_out if point == "in" else updated_in
        if updated_in is not None and updated_out is not None:
            show_status(
                f"{point_label} point disetel pada {chosen:.3f} detik. "
                f"Range {updated_in:.3f}–{updated_out:.3f} detik "
                f"({timeline_in_out_duration_seconds(updated_in, updated_out):.3f} detik)."
            )
        else:
            show_status(
                f"{point_label} point disetel pada {chosen:.3f} detik. "
                "Setel titik pasangannya untuk membuat range."
            )

    def goto_point(point: TimelineRangePoint) -> None:
        in_point, out_point = range_points()
        target = in_point if point == "in" else out_point
        if target is None:
            show_status(
                "In point belum disetel." if point == "in" else "Out point belum disetel."
            )
            return
        seek_global(target)
        show_status(
            f"Playhead dipindah ke {'In' if point == 'in' else 'Out'} point "
            f"{target:.3f} detik."
        )

    class _TimelineInOutKeyFilter(QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:  # noqa: N802
            del watched
            if event.type() != QEvent.Type.KeyPress or not root.isVisible():
                return False
            if event.key() not in (Qt.Key.Key_I, Qt.Key.Key_O):
                return False

            focus = app.focusWidget()
            if isinstance(
                focus,
                (QLineEdit, QAbstractSpinBox, QTextEdit, QPlainTextEdit),
            ):
                return False
            if focus is not None and focus is not root and not root.isAncestorOf(focus):
                return False

            point: TimelineRangePoint = "in" if event.key() == Qt.Key.Key_I else "out"
            modifiers = event.modifiers()
            if modifiers == Qt.KeyboardModifier.NoModifier:
                set_point(point)
            elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                goto_point(point)
            else:
                return False
            event.accept()
            return True

    previous_filter = getattr(root, "_aavc_timeline_in_out_key_filter", None)
    if previous_filter is not None:
        app.removeEventFilter(previous_filter)

    event_filter = _TimelineInOutKeyFilter(root)
    app.installEventFilter(event_filter)
    root._aavc_timeline_in_out_key_filter = event_filter

    zoom_box = root.findChild(QSpinBox, "TimelineZoomPercent")
    if zoom_box is not None:
        zoom_box.valueChanged.connect(lambda _value: refresh_range_widgets())

    ruler.setToolTip(
        f"{ruler.toolTip()} I = set In; O = set Out; Shift+I/O = lompat ke titik. "
        "Range hanya untuk sesi editor ini."
    )
    refresh_range_widgets()
    return True
