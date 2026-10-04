from __future__ import annotations

from pathlib import Path
from typing import Any

from aavc.domain.project.models import AnimationAssignment, ProjectState
from aavc.presentation.motion_preview import (
    native_motion_preview_offset,
    preview_narration_seconds,
    preview_neighbor_scene_index,
    preview_scrub_seconds,
    preview_timecode,
)
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


def _find_preview_timecode_label(root: Any) -> Any | None:
    from PySide6.QtWidgets import QLabel

    for label in root.findChildren(QLabel):
        text = label.text()
        if " / " in text and text.count(":") >= 6:
            return label
    return None


def install_native_motion_preview(root: Any, project: ProjectState) -> bool:
    """Enable visual playback, scrubbing, Scene transport, narration, and live timecode."""

    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QPushButton, QSlider

    scene_list = _find_scene_list(root, project)
    canvas = _find_preview_canvas(root)
    timecode_label = _find_preview_timecode_label(root)
    buttons = root.findChildren(QPushButton)
    previous_button = next((button for button in buttons if button.text() == "◀"), None)
    play_button = next((button for button in buttons if button.text() == "▶"), None)
    next_button = next((button for button in buttons if button.text() == "▶|"), None)
    audio_button = next(
        (button for button in buttons if button.text() in {"🔊", "🔇"}),
        None,
    )
    sliders = root.findChildren(QSlider)
    progress_slider = sliders[0] if sliders else None
    if (
        scene_list is None
        or canvas is None
        or previous_button is None
        or play_button is None
        or next_button is None
    ):
        return False

    previous_button.setToolTip("Pilih Scene sebelumnya pada preview.")
    next_button.setToolTip("Pilih Scene berikutnya pada preview.")
    play_button.setToolTip(
        "Putar preview motion native Rise/Pan/Drift untuk Scene terpilih. "
        "Narasi ikut diputar bila tersedia; subtitle overlay belum aktif."
    )
    if progress_slider is not None:
        progress_slider.setRange(0, 1000)
        progress_slider.setValue(0)
        progress_slider.setToolTip(
            "Geser untuk melihat frame motion dan posisi narasi pada waktu tertentu."
        )

    media_player: Any | None = None
    audio_output: Any | None = None
    audio_muted = False
    narration_path = (
        Path(project.narration_audio).expanduser()
        if project.narration_audio
        else None
    )
    if audio_button is not None:
        if narration_path is not None and narration_path.is_file():
            try:
                from PySide6.QtCore import QUrl
                from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            except ImportError:
                audio_button.setEnabled(False)
                audio_button.setToolTip(
                    "Qt Multimedia tidak tersedia; preview visual tetap dapat digunakan."
                )
            else:
                audio_output = QAudioOutput(root)
                audio_output.setVolume(1.0)
                media_player = QMediaPlayer(root)
                media_player.setAudioOutput(audio_output)
                media_player.setSource(
                    QUrl.fromLocalFile(str(narration_path.resolve()))
                )
                audio_button.setText("🔊")
                audio_button.setToolTip("Mute/unmute narasi preview.")
        else:
            audio_button.setEnabled(False)
            if project.narration_audio:
                audio_button.setToolTip(
                    "File narasi project tidak ditemukan; impor ulang narasi untuk preview audio."
                )
            else:
                audio_button.setToolTip(
                    "Narasi belum diimpor; preview audio belum tersedia."
                )

    timer = QTimer(root)
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    fps = max(1, int(project.fps))
    timer.setInterval(max(15, int(round(1000 / fps))))
    frame_step = 1.0 / fps
    playback_seconds = 0.0
    scene_durations = tuple(scene.duration_seconds for scene in project.scenes)
    total_project_seconds = sum(max(0.0, float(value)) for value in scene_durations)

    def selected_plan() -> ScenePreviewPlan | None:
        row = scene_list.currentRow()
        if row < 0 or row >= len(project.scenes):
            return None
        return build_scene_preview_plan(project, project.scenes[row])

    def narration_seconds(local_seconds: float) -> float:
        return preview_narration_seconds(
            scene_durations,
            scene_list.currentRow(),
            local_seconds,
        )

    def update_timecode(local_seconds: float) -> None:
        if timecode_label is None:
            return
        current = narration_seconds(local_seconds)
        timecode_label.setText(
            f"{preview_timecode(current, fps)}  /  "
            f"{preview_timecode(total_project_seconds, fps)}"
        )

    def seek_audio(local_seconds: float) -> None:
        if media_player is None:
            return
        global_seconds = narration_seconds(local_seconds)
        media_player.setPosition(max(0, int(round(global_seconds * 1000))))

    def pause_audio() -> None:
        if media_player is not None:
            media_player.pause()

    def update_transport_state(row: int) -> None:
        valid_scene = 0 <= row < len(project.scenes)
        previous_button.setEnabled(
            preview_neighbor_scene_index(row, len(project.scenes), -1) is not None
        )
        next_button.setEnabled(
            preview_neighbor_scene_index(row, len(project.scenes), 1) is not None
        )
        play_button.setEnabled(valid_scene)
        if progress_slider is not None:
            progress_slider.setEnabled(valid_scene)
        if audio_button is not None:
            audio_button.setEnabled(valid_scene and media_player is not None)

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
        local_seconds = 0.0 if time_seconds is None else time_seconds
        update_timecode(local_seconds)
        if progress_slider is not None:
            if time_seconds is None or plan.duration_seconds <= 0:
                progress_slider.setValue(0)
            else:
                fraction = max(0.0, min(1.0, time_seconds / plan.duration_seconds))
                progress_slider.setValue(int(round(fraction * 1000)))

    def stop_playback(
        *,
        restore_static: bool = True,
        reset_position: bool = True,
    ) -> None:
        nonlocal playback_seconds
        timer.stop()
        pause_audio()
        if reset_position:
            playback_seconds = 0.0
            seek_audio(0.0)
        play_button.setText("▶")
        if restore_static:
            render_frame(None)
        elif reset_position and progress_slider is not None:
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

        start_seconds = 0.0
        if progress_slider is not None:
            start_seconds = preview_scrub_seconds(
                progress_slider.value(),
                progress_slider.maximum(),
                plan.duration_seconds,
            )
        if start_seconds >= plan.duration_seconds:
            start_seconds = 0.0

        playback_seconds = start_seconds
        play_button.setText("⏸")
        render_frame(playback_seconds)
        seek_audio(playback_seconds)
        if media_player is not None:
            media_player.play()
        timer.start()

    def scrub_to_value(value: int) -> None:
        nonlocal playback_seconds
        if progress_slider is None:
            return
        plan = selected_plan()
        if plan is None:
            return
        timer.stop()
        pause_audio()
        play_button.setText("▶")
        playback_seconds = preview_scrub_seconds(
            value,
            progress_slider.maximum(),
            plan.duration_seconds,
        )
        render_frame(playback_seconds)
        seek_audio(playback_seconds)

    def scrub_started() -> None:
        stop_playback(restore_static=False, reset_position=False)
        if progress_slider is not None:
            scrub_to_value(progress_slider.value())

    def scrub_released() -> None:
        if progress_slider is not None:
            scrub_to_value(progress_slider.value())

    def navigate_scene(step: int) -> None:
        target = preview_neighbor_scene_index(
            scene_list.currentRow(),
            len(project.scenes),
            step,
        )
        if target is not None:
            scene_list.setCurrentRow(target)

    def scene_changed(row: int) -> None:
        stop_playback(restore_static=False)
        update_transport_state(row)
        update_timecode(0.0)

    def toggle_audio() -> None:
        nonlocal audio_muted
        if audio_button is None or audio_output is None:
            return
        audio_muted = not audio_muted
        audio_output.setMuted(audio_muted)
        audio_button.setText("🔇" if audio_muted else "🔊")
        audio_button.setToolTip(
            "Unmute narasi preview." if audio_muted else "Mute narasi preview."
        )

    timer.timeout.connect(tick)
    previous_button.clicked.connect(lambda: navigate_scene(-1))
    play_button.clicked.connect(toggle_playback)
    next_button.clicked.connect(lambda: navigate_scene(1))
    scene_list.currentRowChanged.connect(scene_changed)
    if progress_slider is not None:
        progress_slider.sliderPressed.connect(scrub_started)
        progress_slider.sliderMoved.connect(scrub_to_value)
        progress_slider.sliderReleased.connect(scrub_released)
    if audio_button is not None:
        audio_button.clicked.connect(toggle_audio)
    update_transport_state(scene_list.currentRow())
    update_timecode(0.0)
    seek_audio(0.0)
    return True
