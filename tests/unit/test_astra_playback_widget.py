from __future__ import annotations

import os

import pytest

from aavc.domain.project.models import AssetBinding, ProjectState, Scene
from aavc.presentation.native_motion_playback import install_native_motion_preview

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _project() -> ProjectState:
    scenes = (
        Scene(1, ("A001",), ("one",), 0.4),
        Scene(2, ("A002",), ("two",), 0.3),
        Scene(3, ("A003",), ("three",), 1.0),
    )
    bindings = tuple(
        AssetBinding(
            asset_id=asset_id,
            source_quote=quote,
            path=None,
            status="MISSING",
        )
        for scene in scenes
        for asset_id, quote in zip(scene.asset_ids, scene.source_quotes, strict=True)
    )
    return ProjectState(
        schema_version=2,
        title="astra-playback-widget",
        source_docx="missing.docx",
        asset_directory="missing-assets",
        scenes=scenes,
        bindings=bindings,
        fps=30,
    )


def _preview_root(project: ProjectState):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QListWidget,
        QPushButton,
        QSlider,
        QWidget,
    )

    app = QApplication.instance() or QApplication([])
    root = QWidget()

    scene_list = QListWidget(root)
    for scene in project.scenes:
        scene_list.addItem(f"{scene.scene_number:02d}. Scene")
    scene_list.setCurrentRow(0)

    canvas = QLabel(root)
    canvas.setMinimumSize(640, 360)
    timecode = QLabel("00:00:00:00  /  00:00:01:21", root)

    QPushButton("◀", root)
    play_button = QPushButton("▶", root)
    QPushButton("▶|", root)
    slider = QSlider(Qt.Orientation.Horizontal, root)

    assert install_native_motion_preview(root, project)
    root._test_qapp = app
    return root, scene_list, play_button, slider, timecode


def test_delayed_redraw_pause_and_resume_preserve_real_playback_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtCore import QTimer

    now = [100.0]
    monkeypatch.setattr(
        "aavc.presentation.native_motion_playback.time.monotonic",
        lambda: now[0],
    )

    root, scene_list, play_button, slider, timecode = _preview_root(_project())
    timers = root.findChildren(QTimer)
    assert len(timers) == 1
    timer = timers[0]

    play_button.click()
    assert timer.isActive()
    assert play_button.text() == "⏸"

    # A single delayed redraw arrives after 0.95 s. Playback must use elapsed
    # monotonic time, skip the first two short scenes, and retain 0.25 s residual.
    now[0] = 100.95
    timer.timeout.emit()

    assert scene_list.currentRow() == 2
    assert slider.value() == pytest.approx(250, abs=1)
    assert timecode.text().startswith(("00:00:00:28", "00:00:00:29"))

    paused_slider = slider.value()
    paused_timecode = timecode.text()
    play_button.click()

    assert not timer.isActive()
    assert play_button.text() == "▶"
    assert slider.value() == paused_slider
    assert timecode.text() == paused_timecode

    # Even if a timeout callback is emitted manually after one second paused,
    # the transport must remain at the paused frame.
    now[0] = 101.95
    timer.timeout.emit()
    assert slider.value() == paused_slider
    assert timecode.text() == paused_timecode

    play_button.click()
    assert timer.isActive()
    now[0] = 102.25
    timer.timeout.emit()

    assert scene_list.currentRow() == 2
    assert slider.value() > paused_slider
    assert timecode.text() != paused_timecode
    root.deleteLater()
