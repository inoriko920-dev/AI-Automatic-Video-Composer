from __future__ import annotations

from typing import Any

from aavc.domain.project.models import AnimationAssignment, ProjectState
from aavc.presentation.motion_preview import native_motion_preview_offset
from aavc.presentation.scene_preview import ScenePreviewPlan, build_scene_preview_plan


def _draw_missing_asset(painter: Any, asset: Any, width: int, height: int) -> None:
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QColor, QPen

    box_w = max(160, int(width * asset.max_width * 0.82))
    box_h = max(120, int(height * asset.max_height * 0.72))
    x = int(width * asset.anchor_x - box_w / 2)
    y = int(height * asset.anchor_y - box_h / 2)
    rect = QRectF(x, y, box_w, box_h)
    painter.setPen(QPen(QColor("#D97706"), 3))
    painter.setBrush(QColor("#FFFBEB"))
    painter.drawRoundedRect(rect, 12, 12)
    painter.setPen(QColor("#92400E"))
    painter.drawText(
        rect,
        int(Qt.AlignmentFlag.AlignCenter),
        f"{asset.asset_id}\n{asset.status}\nFile tidak tersedia",
    )


def render_native_motion_pixmap(
    plan: ScenePreviewPlan,
    assignments: tuple[AnimationAssignment, ...],
    *,
    time_seconds: float | None,
    width: int = 1280,
    height: int = 720,
) -> Any:
    """Render one preview frame; None time renders the canonical static layout."""

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPainter, QPixmap

    assignment_by_asset = {
        item.asset_id: item
        for item in assignments
        if item.scene_number == plan.scene_number
    }
    canvas = QPixmap(width, height)
    canvas.fill(QColor("#F4F7FB"))
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    for asset in plan.assets:
        if asset.status != "READY" or asset.path is None:
            _draw_missing_asset(painter, asset, width, height)
            continue
        source = QPixmap(asset.path)
        if source.isNull():
            _draw_missing_asset(painter, asset, width, height)
            continue

        max_width = max(1, int(width * asset.max_width))
        max_height = max(1, int(height * asset.max_height))
        scaled = source.scaled(
            max_width,
            max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = int(width * asset.anchor_x - scaled.width() / 2)
        y = int(height * asset.anchor_y - scaled.height() / 2)
        if time_seconds is not None:
            offset = native_motion_preview_offset(
                assignment_by_asset.get(asset.asset_id),
                time_seconds=time_seconds,
                duration_seconds=plan.duration_seconds,
            )
            x += int(round(width * offset.x))
            y += int(round(height * offset.y))
        painter.drawPixmap(x, y, scaled)

    painter.end()
    return canvas


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


def _find_preview_canvas(root: Any) -> Any | None:
    from PySide6.QtWidgets import QLabel

    for label in root.findChildren(QLabel):
        minimum = label.minimumSize()
        if minimum.width() >= 640 and minimum.height() >= 360:
            return label
    return None


def install_native_motion_preview(root: Any, project: ProjectState) -> bool:
    """Enable native visual playback on a live editor root without mutating project state."""

    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtWidgets import QPushButton, QSlider

    scene_list = _find_scene_list(root, project)
    canvas = _find_preview_canvas(root)
    play_button = next(
        (button for button in root.findChildren(QPushButton) if button.text() == "▶"),
        None,
    )
    sliders = root.findChildren(QSlider)
    progress_slider = sliders[0] if sliders else None
    if scene_list is None or canvas is None or play_button is None:
        return False

    play_button.setEnabled(scene_list.currentRow() >= 0)
    play_button.setToolTip(
        "Putar preview motion native Rise/Pan/Drift untuk Scene terpilih. "
        "Audio, subtitle overlay, dan scrub belum aktif."
    )
    if progress_slider is not None:
        progress_slider.setRange(0, 1000)
        progress_slider.setValue(0)
        progress_slider.setEnabled(False)
        progress_slider.setToolTip(
            "Indikator progress preview. Scrubbing manual belum aktif."
        )

    timer = QTimer(root)
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    fps = max(1, int(project.fps))
    timer.setInterval(max(15, int(round(1000 / fps))))
    frame_step = 1.0 / fps
    playback_seconds = 0.0

    def selected_plan() -> ScenePreviewPlan | None:
        row = scene_list.currentRow()
        if row < 0 or row >= len(project.scenes):
            return None
        return build_scene_preview_plan(project, project.scenes[row])

    def render_frame(time_seconds: float | None) -> None:
        plan = selected_plan()
        if plan is None:
            return
        canvas.setPixmap(
            render_native_motion_pixmap(
                plan,
                project.animations,
                time_seconds=time_seconds,
            )
        )
        if progress_slider is not None:
            if time_seconds is None or plan.duration_seconds <= 0:
                progress_slider.setValue(0)
            else:
                fraction = max(0.0, min(1.0, time_seconds / plan.duration_seconds))
                progress_slider.setValue(int(round(fraction * 1000)))

    def stop_playback(*, restore_static: bool = True) -> None:
        nonlocal playback_seconds
        timer.stop()
        playback_seconds = 0.0
        play_button.setText("▶")
        if restore_static:
            render_frame(None)
        elif progress_slider is not None:
            progress_slider.setValue(0)

    def tick() -> None:
        nonlocal playback_seconds
        plan = selected_plan()
        if plan is None:
            stop_playback(restore_static=False)
            return
        playback_seconds += frame_step
        if playback_seconds >= plan.duration_seconds:
            stop_playback()
            return
        render_frame(playback_seconds)

    def toggle_playback() -> None:
        nonlocal playback_seconds
        plan = selected_plan()
        if plan is None:
            return
        if timer.isActive():
            stop_playback()
            return
        playback_seconds = 0.0
        play_button.setText("⏸")
        render_frame(0.0)
        timer.start()

    def scene_changed(row: int) -> None:
        stop_playback(restore_static=False)
        play_button.setEnabled(0 <= row < len(project.scenes))

    timer.timeout.connect(tick)
    play_button.clicked.connect(toggle_playback)
    scene_list.currentRowChanged.connect(scene_changed)
    return True
