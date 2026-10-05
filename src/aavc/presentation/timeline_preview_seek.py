from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aavc.domain.project.models import ProjectState


def timeline_seek_slider_value(
    position_x: float,
    width: float,
    maximum: int,
) -> int:
    """Map a horizontal click inside a timeline Scene block to preview slider value."""

    span = float(width)
    upper = int(maximum)
    if span <= 0 or upper <= 0:
        return 0
    fraction = max(0.0, min(1.0, float(position_x) / span))
    return int(round(fraction * upper))


def timeline_drag_target_index(
    pointer_x: float,
    button_center_xs: tuple[float, ...],
) -> int:
    """Return the nearest Scene index for a horizontal drag pointer position."""

    if not button_center_xs:
        return -1
    return min(
        range(len(button_center_xs)),
        key=lambda index: abs(float(pointer_x) - float(button_center_xs[index])),
    )


def _find_scene_list(root: Any, project: ProjectState) -> Any | None:
    from PySide6.QtWidgets import QListWidget

    for listing in root.findChildren(QListWidget):
        if listing.count() != len(project.scenes) or not project.scenes:
            continue
        first = listing.item(0)
        if first is not None and first.text().startswith(
            f"{project.scenes[0].scene_number:02d}. Scene"
        ):
            return listing
    return None


def install_timeline_preview_seek(
    root: Any,
    project: ProjectState,
    *,
    on_scene_reordered: Callable[[int, int], None] | None = None,
) -> bool:
    """Seek preview on click and optionally reorder Scene blocks with horizontal drag."""

    from PySide6.QtCore import QEvent, QObject, Qt
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QSlider

    scene_list = _find_scene_list(root, project)
    sliders = root.findChildren(QSlider)
    progress_slider = sliders[0] if sliders else None
    if scene_list is None or progress_slider is None or not project.scenes:
        return False

    active_scene_list: Any = scene_list
    active_slider: Any = progress_slider
    button_indexes: dict[int, int] = {}
    timeline_buttons: list[Any] = []
    buttons = root.findChildren(QPushButton)
    for index, scene in enumerate(project.scenes):
        prefix = f"Sc{scene.scene_number:02d}\n"
        button = next(
            (candidate for candidate in buttons if candidate.text().startswith(prefix)),
            None,
        )
        if button is None:
            continue
        button_indexes[id(button)] = index
        timeline_buttons.append(button)
        if on_scene_reordered is None:
            button.setToolTip(
                f"Scene {scene.scene_number:02d}. Klik posisi pada blok untuk seek preview. "
                "Timeline tetap read-only untuk editing."
            )
        else:
            button.setToolTip(
                f"Scene {scene.scene_number:02d}. Klik posisi untuk seek preview; "
                "drag horizontal untuk mengubah urutan Scene."
            )

    if not timeline_buttons:
        return False

    if on_scene_reordered is not None:
        for label in root.findChildren(QLabel):
            if label.text() == "Timeline Scene · Read-only":
                label.setText("Timeline Scene · Drag untuk reorder")
            elif label.text().startswith("Lebar blok mengikuti durasi scene."):
                label.setText(
                    "Lebar blok mengikuti durasi scene. Klik untuk seek; drag untuk reorder. "
                    "Trim, split, dan resize belum aktif."
                )

    class _TimelineSeekFilter(QObject):
        def __init__(self, parent: Any) -> None:
            super().__init__(parent)
            self._pressed_button_id: int | None = None
            self._press_global_x = 0.0
            self._dragging = False

        def _reset_drag(self, watched: Any) -> None:
            self._pressed_button_id = None
            self._press_global_x = 0.0
            self._dragging = False
            watched.unsetCursor()
            if hasattr(watched, "setDown"):
                watched.setDown(False)

        def eventFilter(self, watched: Any, event: Any) -> bool:  # noqa: N802
            scene_index = button_indexes.get(id(watched))
            if scene_index is None:
                return False

            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._pressed_button_id = id(watched)
                self._press_global_x = float(event.globalPosition().x())
                self._dragging = False
                return False

            if (
                event.type() == QEvent.Type.MouseMove
                and self._pressed_button_id == id(watched)
                and bool(event.buttons() & Qt.MouseButton.LeftButton)
                and on_scene_reordered is not None
            ):
                distance = abs(float(event.globalPosition().x()) - self._press_global_x)
                if distance >= QApplication.startDragDistance():
                    self._dragging = True
                    watched.setCursor(Qt.CursorShape.ClosedHandCursor)
                    return True
                return False

            if (
                event.type() != QEvent.Type.MouseButtonRelease
                or event.button() != Qt.MouseButton.LeftButton
            ):
                return False

            if self._pressed_button_id != id(watched):
                self._reset_drag(watched)
                return False

            if self._dragging and on_scene_reordered is not None:
                pointer_x = float(event.globalPosition().x())
                centers = tuple(
                    float(button.mapToGlobal(button.rect().center()).x())
                    for button in timeline_buttons
                )
                target_index = timeline_drag_target_index(pointer_x, centers)
                source_scene_number = project.scenes[scene_index].scene_number
                self._reset_drag(watched)
                if target_index >= 0 and target_index != scene_index:
                    on_scene_reordered(source_scene_number, target_index)
                return True

            self._reset_drag(watched)
            active_scene_list.setCurrentRow(scene_index)
            value = timeline_seek_slider_value(
                event.position().x(),
                watched.width(),
                active_slider.maximum(),
            )
            active_slider.setValue(value)
            active_slider.sliderMoved.emit(value)
            return False

    event_filter = _TimelineSeekFilter(root)
    for button in timeline_buttons:
        button.installEventFilter(event_filter)
    root._aavc_timeline_seek_filter = event_filter
    return True
