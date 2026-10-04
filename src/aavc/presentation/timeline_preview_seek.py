from __future__ import annotations

from typing import Any

from aavc.domain.project.models import ProjectState


def timeline_seek_slider_value(
    position_x: float,
    width: float,
    maximum: int,
) -> int:
    """Map a horizontal click inside a timeline Scene block to preview slider value."""

    span = float(width)
    if span <= 0:
        return 0
    upper = max(1, int(maximum))
    fraction = max(0.0, min(1.0, float(position_x) / span))
    return int(round(fraction * upper))


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


def install_timeline_preview_seek(root: Any, project: ProjectState) -> bool:
    """Seek the existing preview controller from horizontal clicks on Scene blocks."""

    from PySide6.QtCore import QEvent, QObject, Qt
    from PySide6.QtWidgets import QPushButton, QSlider

    scene_list = _find_scene_list(root, project)
    sliders = root.findChildren(QSlider)
    progress_slider = sliders[0] if sliders else None
    if scene_list is None or progress_slider is None or not project.scenes:
        return False

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
        button.setToolTip(
            f"Scene {scene.scene_number:02d}. Klik posisi pada blok untuk seek preview. "
            "Timeline tetap read-only untuk editing."
        )

    if not timeline_buttons:
        return False

    class _TimelineSeekFilter(QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:  # noqa: N802
            if (
                event.type() != QEvent.Type.MouseButtonRelease
                or event.button() != Qt.MouseButton.LeftButton
            ):
                return False
            scene_index = button_indexes.get(id(watched))
            if scene_index is None:
                return False

            scene_list.setCurrentRow(scene_index)
            value = timeline_seek_slider_value(
                event.position().x(),
                watched.width(),
                progress_slider.maximum(),
            )
            progress_slider.setValue(value)
            progress_slider.sliderMoved.emit(value)
            return False

    event_filter = _TimelineSeekFilter(root)
    for button in timeline_buttons:
        button.installEventFilter(event_filter)
    setattr(root, "_aavc_timeline_seek_filter", event_filter)
    return True
