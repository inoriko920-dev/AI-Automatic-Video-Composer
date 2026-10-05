from __future__ import annotations

from typing import Any

from aavc.application.commands import RemoveAnimationAssignment, SetAnimationAssignment
from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.dialogs.asset_motion import show_asset_motion_dialog
from aavc.presentation.windows.project_menu_window import ProjectMenuMainWindow


def animation_menu_enabled(*, has_project: bool, has_selected_scene: bool) -> bool:
    """Return whether the live asset-motion editor may be opened."""

    return has_project and has_selected_scene


class AnimationMenuMainWindow(ProjectMenuMainWindow):
    """Expose render-backed per-asset motion through the runtime Animation menu."""

    def __init__(
        self,
        services: FoundationServices,
        initial_state: str = "UI-002",
    ) -> None:
        self._asset_motion_action: Any | None = None
        super().__init__(services, initial_state=initial_state)

    def _build_menu(self, action_type: Any) -> None:
        super()._build_menu(action_type)

        animation_menu: Any | None = None
        for menu_action in self.window.menuBar().actions():
            if menu_action.text() == "Animasi":
                animation_menu = menu_action.menu()
                break
        if animation_menu is None:
            return

        animation_menu.clear()
        asset_motion = action_type("Animasi Aset Scene Terpilih…", self.window)
        asset_motion.setObjectName("AssetMotionAction")
        asset_motion.triggered.connect(
            lambda _checked=False: self.edit_selected_scene_asset_motion()
        )
        animation_menu.addAction(asset_motion)
        self._asset_motion_action = asset_motion
        self._refresh_animation_menu_state()

    def _refresh_animation_menu_state(self) -> None:
        action = self._asset_motion_action
        if action is None:
            return
        project = self.services.project_session.current
        selected_scene = self._selected_scene_number
        action.setEnabled(
            animation_menu_enabled(
                has_project=project is not None,
                has_selected_scene=selected_scene is not None,
            )
        )

    def _remember_selected_scene(self, scene_number: int) -> None:
        super()._remember_selected_scene(scene_number)
        self._refresh_animation_menu_state()

    def edit_selected_scene_asset_motion(self) -> None:
        session = self.services.project_session
        project = session.current
        scene_number = self._selected_scene_number
        if project is None or scene_number is None:
            self._show_project_notice(
                "Animasi Aset tidak tersedia",
                "Buat atau buka proyek, lalu pilih Scene terlebih dahulu.",
            )
            self._refresh_animation_menu_state()
            return

        scene = next(
            (item for item in project.scenes if item.scene_number == scene_number),
            None,
        )
        if scene is None:
            self._show_project_notice(
                "Scene tidak ditemukan",
                "Pilih ulang Scene sebelum mengatur animasi aset.",
            )
            return

        result = show_asset_motion_dialog(self.window, scene, project.animations)
        if result is None:
            return

        try:
            if result.action == "apply":
                if result.assignment is None:
                    raise ValueError("Assignment animasi tidak tersedia")
                updated = session.execute(SetAnimationAssignment(result.assignment))
                assignment = next(
                    item
                    for item in updated.animations
                    if item.scene_number == scene_number
                    and item.asset_id == result.asset_id
                )
                message = (
                    f"Animasi {result.asset_id} diterapkan: "
                    f"{assignment.enter_effect} → {assignment.exit_effect}. "
                    "Klik Simpan untuk menyimpan perubahan."
                )
            else:
                session.execute(RemoveAnimationAssignment(scene_number, result.asset_id))
                message = (
                    f"Animasi {result.asset_id} dihapus. "
                    "Klik Simpan untuk menyimpan perubahan."
                )
        except ValueError as error:
            self._show_project_error("Gagal mengubah animasi aset", error)
            return

        self._refresh_window_title()
        self.refresh_editor_overview()
        self._refresh_animation_menu_state()
        self.window.statusBar().showMessage(message, 7000)


def create_animation_menu_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> AnimationMenuMainWindow:
    return AnimationMenuMainWindow(services, initial_state=initial_state)
