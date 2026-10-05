from __future__ import annotations

from aavc.application.commands import MoveSceneToIndex
from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.native_motion_playback import install_native_motion_preview
from aavc.presentation.navigation import UiRoute
from aavc.presentation.timeline_preview_seek import install_timeline_preview_seek
from aavc.presentation.windows.native_motion_window import NativeMotionMainWindow


class NativeMotionPreviewMainWindow(NativeMotionMainWindow):
    """Native-motion editor with non-destructive selected-scene playback preview."""

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


def create_native_motion_preview_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> NativeMotionPreviewMainWindow:
    return NativeMotionPreviewMainWindow(services, initial_state=initial_state)
