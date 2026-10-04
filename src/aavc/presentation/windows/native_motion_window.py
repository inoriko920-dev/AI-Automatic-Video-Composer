from __future__ import annotations

from typing import Any

from aavc.application.commands import (
    RemoveAnimationAssignment,
    SetAnimationAssignment,
)
from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.dialogs.asset_motion import show_asset_motion_dialog
from aavc.presentation.windows.guarded_main_window import GuardedMainWindow


class NativeMotionMainWindow(GuardedMainWindow):
    """Guarded editor shell with render-backed phase-one asset motion controls."""

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
        motion_action = action_type("Animasi Aset…", self.window)
        motion_action.triggered.connect(
            lambda _checked=False: self.open_asset_motion_editor()
        )
        edit_menu.addAction(motion_action)

    def open_asset_motion_editor(self) -> None:
        session = self.services.project_session
        project = session.current
        if project is None:
            self._show_project_notice(
                "Animasi Aset tidak tersedia",
                "Buat atau buka proyek terlebih dahulu.",
            )
            return

        scene_number = self._selected_scene_number
        if scene_number is None:
            self.window.statusBar().showMessage(
                "Pilih Scene terlebih dahulu sebelum mengatur animasi aset.",
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

        result = show_asset_motion_dialog(
            self.window,
            scene,
            project.animations,
        )
        if result is None:
            return

        try:
            if result.action == "apply":
                if result.assignment is None:
                    raise ValueError("Assignment animasi tidak tersedia")
                session.execute(SetAnimationAssignment(result.assignment))
                message = (
                    f"Animasi {result.asset_id} diterapkan pada Scene {scene_number:02d}. "
                    "Klik Simpan untuk menyimpan perubahan."
                )
            else:
                session.execute(
                    RemoveAnimationAssignment(scene_number, result.asset_id)
                )
                message = (
                    f"Animasi {result.asset_id} dihapus dari Scene {scene_number:02d}. "
                    "Klik Simpan untuk menyimpan perubahan."
                )
        except ValueError as error:
            self._show_project_error("Gagal mengubah animasi aset", error)
            return

        self._selected_scene_number = scene_number
        self._refresh_window_title()
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        self.window.statusBar().showMessage(message, 7000)


def create_native_motion_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> NativeMotionMainWindow:
    return NativeMotionMainWindow(services, initial_state=initial_state)
