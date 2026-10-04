from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from aavc.application.commands.scene_order import MoveScene
from aavc.application.services.vertical_slice import create_project_state
from aavc.bootstrap.composition_root import FoundationServices
from aavc.domain.errors import AAVCError
from aavc.presentation.navigation import UiRoute
from aavc.presentation.windows.main_window import MainWindow, ensure_project_suffix

UnsavedChoice = Literal["save", "discard", "cancel"]


def resolve_unsaved_choice(
    is_dirty: bool,
    choice: UnsavedChoice,
    *,
    save_succeeded: bool = False,
) -> bool:
    """Return whether a destructive action may continue."""

    if not is_dirty:
        return True
    if choice == "discard":
        return True
    if choice == "cancel":
        return False
    if choice == "save":
        return save_succeeded
    raise ValueError(f"Pilihan unsaved-change tidak dikenal: {choice}")


class GuardedMainWindow(MainWindow):
    """Main window that prevents silent loss and exposes safe editor commands."""

    def __init__(
        self,
        services: FoundationServices,
        initial_state: str = "UI-002",
    ) -> None:
        self._allow_close = False
        self._close_guard: object | None = None
        super().__init__(services, initial_state=initial_state)
        self._install_close_guard()

    def _build_menu(self, action_type: Any) -> None:
        super()._build_menu(action_type)

        edit_menu: Any | None = None
        for menu_action in self.window.menuBar().actions():
            if menu_action.text() == "Edit":
                edit_menu = menu_action.menu()
                break
        if edit_menu is None:
            return

        edit_menu.clear()

        undo_action = action_type("Undo", self.window)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_project)
        edit_menu.addAction(undo_action)

        redo_action = action_type("Redo", self.window)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo_project)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        move_up = action_type("Pindah Scene ke Atas", self.window)
        move_up.setShortcut("Alt+Up")
        move_up.triggered.connect(
            lambda _checked=False: self.move_selected_scene(-1)
        )
        edit_menu.addAction(move_up)

        move_down = action_type("Pindah Scene ke Bawah", self.window)
        move_down.setShortcut("Alt+Down")
        move_down.triggered.connect(
            lambda _checked=False: self.move_selected_scene(1)
        )
        edit_menu.addAction(move_down)

    def _install_close_guard(self) -> None:
        from PySide6.QtCore import QEvent, QObject

        owner = self

        class CloseGuard(QObject):
            def eventFilter(self, watched: Any, event: Any) -> bool:
                if watched is owner.window and event.type() == QEvent.Type.Close:
                    if owner._allow_close:
                        return False
                    if not owner._confirm_unsaved_changes("keluar dari aplikasi"):
                        event.ignore()
                        return True
                    owner._allow_close = True
                return False

        guard = CloseGuard(self.window)
        self.window.installEventFilter(guard)
        self._close_guard = guard

    def _confirm_unsaved_changes(self, action_label: str) -> bool:
        from PySide6.QtWidgets import QMessageBox

        session = self.services.project_session
        if not session.is_dirty:
            return True

        project = session.current
        project_title = project.title if project is not None else "project aktif"
        box = QMessageBox(self.window)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Perubahan belum disimpan")
        box.setText(f"{project_title} memiliki perubahan yang belum disimpan.")
        box.setInformativeText(f"Simpan perubahan sebelum {action_label}?")
        box.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        box.setDefaultButton(QMessageBox.StandardButton.Save)
        result = QMessageBox.StandardButton(box.exec())

        if result == QMessageBox.StandardButton.Save:
            super().save_project()
            return resolve_unsaved_choice(
                True,
                "save",
                save_succeeded=not session.is_dirty,
            )
        if result == QMessageBox.StandardButton.Discard:
            return resolve_unsaved_choice(True, "discard")
        return resolve_unsaved_choice(True, "cancel")

    def move_selected_scene(self, offset: int) -> None:
        project = self.services.project_session.current
        if project is None:
            self._show_project_notice(
                "Reorder Scene tidak tersedia",
                "Buat atau buka proyek terlebih dahulu.",
            )
            return

        scene_number = self._selected_scene_number
        if scene_number is None:
            self.window.statusBar().showMessage(
                "Pilih Scene terlebih dahulu sebelum mengubah urutan.",
                5000,
            )
            return

        try:
            self.services.project_session.execute(MoveScene(scene_number, offset))
        except ValueError as error:
            self.window.statusBar().showMessage(str(error), 5000)
            return

        self._refresh_window_title()
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        direction = "atas" if offset < 0 else "bawah"
        self.window.statusBar().showMessage(
            f"Scene {scene_number:02d} dipindah satu posisi ke {direction}. "
            "Klik Simpan untuk menyimpan perubahan.",
            7000,
        )

    def open_project(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        chosen, _ = QFileDialog.getOpenFileName(
            self.window,
            "Buka Proyek AAVC",
            "",
            "AAVC Project (*.aavcproj);;Semua File (*.*)",
        )
        if not chosen:
            return
        if not self._confirm_unsaved_changes("membuka project lain"):
            return

        try:
            project = self.services.project_session.open(chosen)
        except (AAVCError, OSError, ValueError, KeyError, TypeError) as error:
            self._show_project_error("Gagal membuka proyek", error)
            return

        self._selected_scene_number = (
            project.scenes[0].scene_number if project.scenes else None
        )
        self._refresh_window_title()
        self.window.statusBar().showMessage(f"Proyek dibuka: {chosen}", 5000)
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        self.show_route(UiRoute.EDITOR)

    def create_project_from_docx(self, scene_docx: str) -> None:
        from PySide6.QtWidgets import QFileDialog

        source = Path(scene_docx).resolve()
        if not source.is_file():
            self._show_project_notice(
                "Scene DOCX belum dipilih",
                "Pilih file Scene DOCX terlebih dahulu.",
            )
            return

        asset_directory = QFileDialog.getExistingDirectory(
            self.window,
            "Pilih Folder Aset",
            str(source.parent),
        )
        if not asset_directory:
            return

        try:
            project = create_project_state(
                title=source.stem,
                scene_docx=source,
                asset_directory=asset_directory,
            )
        except (AAVCError, OSError, ValueError, KeyError, TypeError) as error:
            self._show_project_error("Gagal membaca input proyek", error)
            return

        default_destination = str(source.with_suffix(".aavcproj"))
        destination, _ = QFileDialog.getSaveFileName(
            self.window,
            "Simpan Proyek AAVC",
            default_destination,
            "AAVC Project (*.aavcproj)",
        )
        if not destination:
            return
        destination = ensure_project_suffix(destination)

        if not self._confirm_unsaved_changes("membuat project baru"):
            return

        try:
            self.services.project_session.create(project, destination)
        except (AAVCError, OSError, ValueError) as error:
            self._show_project_error("Gagal menyimpan proyek baru", error)
            return

        self._selected_scene_number = (
            project.scenes[0].scene_number if project.scenes else None
        )
        self._refresh_window_title()
        self.window.statusBar().showMessage(f"Proyek dibuat: {destination}", 5000)
        self._refresh_validation_badge()
        self.refresh_editor_overview()
        self.show_route(UiRoute.EDITOR)


def create_guarded_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> GuardedMainWindow:
    return GuardedMainWindow(services, initial_state=initial_state)
