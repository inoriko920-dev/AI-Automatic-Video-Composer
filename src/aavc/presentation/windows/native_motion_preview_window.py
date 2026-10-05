from __future__ import annotations

from typing import Any

from aavc.application.commands import MoveSceneToIndex, SplitScene
from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.motion_preview import preview_scrub_seconds
from aavc.presentation.native_motion_playback import install_native_motion_preview
from aavc.presentation.navigation import UiRoute
from aavc.presentation.timeline_preview_seek import install_timeline_preview_seek
from aavc.presentation.timeline_ruler_seek import install_timeline_ruler_seek
from aavc.presentation.timeline_zoom_scroll import install_timeline_zoom_scroll
from aavc.presentation.windows.native_motion_window import NativeMotionMainWindow


def scene_split_seconds_from_slider(
    value: int,
    maximum: int,
    duration_seconds: float,
) -> float:
    """Map the editor playhead slider to a millisecond-precision Scene split point."""

    return round(preview_scrub_seconds(value, maximum, duration_seconds), 3)


class NativeMotionPreviewMainWindow(NativeMotionMainWindow):
    """Native-motion editor with playback plus direct timeline Scene editing."""

    def _build_menu(self, action_type: Any) -> None:
        super()._build_menu(action_type)

        edit_menu: Any | None = None
        for menu_action in self.window.menuBar().actions():
            if menu_action.text() == "Edit":
                edit_menu = menu_action.menu()
                break
        if edit_menu is None:
            return

        edit_menu.addSeparator()
        split_action = action_type("Split Scene di Playhead", self.window)
        split_action.setShortcut("Ctrl+B")
        split_action.triggered.connect(
            lambda _checked=False: self.split_selected_scene_at_playhead()
        )
        edit_menu.addAction(split_action)

    def move_scene_to_index(self, scene_number: int, target_index: int) -> None:
        project = self.services.project_session.current
        if project is None:
            return

        source_index = next(
            (
                index
                for index, scene in enumerate(project.scenes)
                if scene.scene_number == scene_number
            ),
            None,
        )
        if source_index is None or source_index == target_index:
            return

        try:
            self.services.project_session.execute(
                MoveSceneToIndex(scene_number, target_index)
            )
        except ValueError as error:
            self.window.statusBar().showMessage(str(error), 5000)
            return

        self._selected_scene_number = scene_number
        self._refresh_window_title()
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        self.window.statusBar().showMessage(
            f"Scene {scene_number:02d} dipindah ke posisi {target_index + 1} melalui timeline. "
            "Klik Simpan untuk menyimpan perubahan.",
            7000,
        )

    def split_selected_scene_at_playhead(self) -> None:
        from PySide6.QtWidgets import QSlider

        session = self.services.project_session
        project = session.current
        if project is None:
            self._show_project_notice(
                "Split Scene tidak tersedia",
                "Buat atau buka proyek terlebih dahulu.",
            )
            return

        scene_number = self._selected_scene_number
        if scene_number is None:
            self.window.statusBar().showMessage(
                "Pilih Scene terlebih dahulu sebelum melakukan Split.",
                5000,
            )
            return

        scene = next(
            (item for item in project.scenes if item.scene_number == scene_number),
            None,
        )
        if scene is None:
            self.window.statusBar().showMessage(
                f"Scene {scene_number} tidak ditemukan.",
                5000,
            )
            return

        root = self._route_widgets.get(UiRoute.EDITOR)
        if root is None:
            self.window.statusBar().showMessage(
                "Buka Editor untuk menentukan posisi playhead Split.",
                5000,
            )
            return
        sliders = root.findChildren(QSlider)
        progress_slider = sliders[0] if sliders else None
        if progress_slider is None:
            self.window.statusBar().showMessage(
                "Playhead preview tidak tersedia pada Editor aktif.",
                5000,
            )
            return

        split_seconds = scene_split_seconds_from_slider(
            progress_slider.value(),
            progress_slider.maximum(),
            scene.duration_seconds,
        )
        new_scene_number = max(item.scene_number for item in project.scenes) + 1
        try:
            session.execute(SplitScene(scene_number, split_seconds))
        except ValueError as error:
            self.window.statusBar().showMessage(
                f"Split tidak dilakukan: {error}. Geser playhead ke bagian tengah Scene.",
                7000,
            )
            return

        self._selected_scene_number = scene_number
        self._refresh_window_title()
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        self.window.statusBar().showMessage(
            f"Scene {scene_number:02d} di-split pada {split_seconds:.3f} detik; "
            f"bagian kedua menjadi Scene {new_scene_number:02d}. "
            "Gunakan Undo untuk membatalkan atau klik Simpan untuk menyimpan perubahan.",
            9000,
        )

    def _mark_split_available(self, root: Any) -> None:
        from PySide6.QtWidgets import QLabel, QSlider

        for label in root.findChildren(QLabel):
            text = label.text()
            if "Split belum aktif." in text:
                label.setText(
                    text.replace(
                        "Split belum aktif.",
                        "Split: Ctrl+B pada playhead.",
                    )
                )
            elif "Split dan trim kiri belum aktif." in text:
                label.setText(
                    text.replace(
                        "Split dan trim kiri belum aktif.",
                        "Split: Ctrl+B pada playhead. Trim kiri belum aktif.",
                    )
                )
        sliders = root.findChildren(QSlider)
        if sliders:
            sliders[0].setToolTip(
                f"{sliders[0].toolTip()} Gunakan Ctrl+B untuk Split Scene pada posisi ini."
            )

    def refresh_editor_overview(self) -> None:
        super().refresh_editor_overview()
        project = self.services.project_session.current
        if project is None:
            return
        root = self._route_widgets.get(UiRoute.EDITOR)
        if root is not None:
            install_native_motion_preview(root, project)
            install_timeline_preview_seek(
                root,
                project,
                on_scene_reordered=self.move_scene_to_index,
                on_scene_resized=self.set_scene_duration,
            )
            self._mark_split_available(root)
            install_timeline_zoom_scroll(root, project)
            install_timeline_ruler_seek(root, project)


def create_native_motion_preview_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> NativeMotionPreviewMainWindow:
    return NativeMotionPreviewMainWindow(services, initial_state=initial_state)
