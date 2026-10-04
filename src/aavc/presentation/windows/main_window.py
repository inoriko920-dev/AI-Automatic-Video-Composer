from __future__ import annotations

from pathlib import Path
from typing import Any

from aavc.bootstrap.composition_root import FoundationServices
from aavc.domain.errors import AAVCError
from aavc.presentation.design_tokens import METRICS, app_stylesheet
from aavc.presentation.navigation import UiRoute, parse_route


def pending_feature_message(feature: str) -> tuple[str, str]:
    return (
        "Fitur belum terhubung",
        f"{feature} belum terhubung ke sesi proyek pada build ini. "
        "Tidak ada perubahan proyek yang dilakukan.",
    )


def ensure_project_suffix(path: str) -> str:
    return path if Path(path).suffix.lower() == ".aavcproj" else f"{path}.aavcproj"


class MainWindow:
    def __init__(self, services: FoundationServices, initial_state: str = "UI-002") -> None:
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import QMainWindow, QStackedWidget, QToolBar

        self.services = services
        self.window = QMainWindow()
        self.window.setObjectName("AAVCMainWindow")
        self.window.setWindowTitle(f"{services.app_name} — Project: Liburan ke Bromo")
        self.window.resize(1600, 900)
        self.window.setMinimumSize(1280, 720)
        self.window.setStyleSheet(app_stylesheet())
        self.stack = QStackedWidget()
        self.window.setCentralWidget(self.stack)
        self._route_widgets: dict[UiRoute, Any] = {}
        self._active_dialog: Any | None = None
        self._toolbar: Any | None = None
        self._build_menu(QAction)
        self._build_toolbar(QToolBar, QAction)
        self._build_pages()
        self.show_route(parse_route(initial_state))

    def _show_pending_feature(self, feature: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        title, message = pending_feature_message(feature)
        QMessageBox.information(self.window, title, message)

    def _show_project_error(self, title: str, error: Exception) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(self.window, title, str(error))

    def _show_project_notice(self, title: str, message: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, title, message)

    def create_project_from_docx(self, scene_docx: str) -> None:
        from PySide6.QtWidgets import QFileDialog

        from aavc.application.services.vertical_slice import create_project_state

        source = Path(scene_docx).resolve()
        if not source.is_file():
            self._show_project_notice("Scene DOCX belum dipilih", "Pilih file Scene DOCX terlebih dahulu.")
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

        try:
            self.services.project_session.create(project, destination)
        except (AAVCError, OSError, ValueError) as error:
            self._show_project_error("Gagal menyimpan proyek baru", error)
            return

        self.window.setWindowTitle(f"{self.services.app_name} — Project: {project.title}")
        self.window.statusBar().showMessage(f"Proyek dibuat: {destination}", 5000)
        self.show_route(UiRoute.EDITOR)

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
        try:
            project = self.services.project_session.open(chosen)
        except (AAVCError, OSError, ValueError, KeyError, TypeError) as error:
            self._show_project_error("Gagal membuka proyek", error)
            return
        self.window.setWindowTitle(f"{self.services.app_name} — Project: {project.title}")
        self.window.statusBar().showMessage(f"Proyek dibuka: {chosen}", 5000)
        self.show_route(UiRoute.EDITOR)

    def save_project(self) -> None:
        try:
            saved = self.services.project_session.save()
        except ValueError as error:
            self._show_project_notice("Simpan tidak tersedia", str(error))
            return
        except (AAVCError, OSError) as error:
            self._show_project_error("Gagal menyimpan proyek", error)
            return
        self.window.statusBar().showMessage(f"Proyek disimpan: {saved}", 5000)

    def undo_project(self) -> None:
        try:
            self.services.project_session.undo()
        except ValueError as error:
            self.window.statusBar().showMessage(f"Undo tidak tersedia: {error}", 5000)
            return
        self.window.statusBar().showMessage("Undo berhasil", 3000)

    def redo_project(self) -> None:
        try:
            self.services.project_session.redo()
        except ValueError as error:
            self.window.statusBar().showMessage(f"Redo tidak tersedia: {error}", 5000)
            return
        self.window.statusBar().showMessage("Redo berhasil", 3000)

    def _build_menu(self, action_type: Any) -> None:
        menu_bar = self.window.menuBar()
        for name in [
            "File",
            "Edit",
            "Proyek",
            "Tampilan",
            "Animasi",
            "AI",
            "Ekspor",
            "Bantuan",
        ]:
            menu = menu_bar.addMenu(name)
            if name == "File":
                new_action = action_type("Proyek Baru", self.window)
                new_action.triggered.connect(
                    lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX)
                )
                menu.addAction(new_action)
                open_action = action_type("Buka Proyek", self.window)
                open_action.triggered.connect(self.open_project)
                menu.addAction(open_action)
                menu.addSeparator()
                save_action = action_type("Simpan", self.window)
                save_action.triggered.connect(self.save_project)
                menu.addAction(save_action)
                exit_action = action_type("Keluar", self.window)
                exit_action.triggered.connect(self.window.close)
                menu.addAction(exit_action)
            elif name == "Ekspor":
                export_action = action_type("Ekspor Video", self.window)
                export_action.triggered.connect(self.open_export)
                menu.addAction(export_action)
            elif name == "Bantuan":
                help_action = action_type("Shortcut & Bantuan Cepat", self.window)
                help_action.triggered.connect(
                    lambda: self._show_pending_feature("Shortcut & Bantuan Cepat")
                )
                menu.addAction(help_action)
            else:
                placeholder_action = action_type(f"{name} — menu", self.window)
                placeholder_action.triggered.connect(
                    lambda _checked=False, feature=name: self._show_pending_feature(
                        f"Menu {feature}"
                    )
                )
                menu.addAction(placeholder_action)

    def _build_toolbar(self, toolbar_type: Any, action_type: Any) -> None:
        from PySide6.QtWidgets import (
            QComboBox,
            QLabel,
            QPushButton,
            QSizePolicy,
            QWidget,
        )

        toolbar = toolbar_type("Utama", self.window)
        toolbar.setMovable(False)
        toolbar.setFixedHeight(METRICS.toolbar_h)
        actions = [
            ("Baru", lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX)),
            ("Buka", self.open_project),
            ("Simpan", self.save_project),
            ("Undo", self.undo_project),
            ("Redo", self.redo_project),
            ("Impor Media", lambda: self._show_pending_feature("Impor Media")),
            ("Tambah Teks", lambda: self.show_route(UiRoute.SUBTITLE_EDITOR)),
            ("Rekam Narasi", lambda: self._show_pending_feature("Rekam Narasi")),
        ]
        for text, callback in actions:
            action = action_type(text, self.window)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Mode Animasi"))
        animation_mode = QComboBox()
        animation_mode.addItems(["Auto (AI)", "Random App", "Manual"])
        animation_mode.setMaximumWidth(130)
        toolbar.addWidget(animation_mode)

        validation = QPushButton("✓ Validasi OK")
        validation.setStyleSheet(
            "color:#15803D; background:#F0FDF4; border:1px solid #BBF7D0; "
            "border-radius:6px; padding:5px 9px; font-weight:600;"
        )
        validation.clicked.connect(lambda: self.show_route(UiRoute.VALIDATION_CENTER))
        toolbar.addWidget(validation)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        export_button = QPushButton("Ekspor Video")
        export_button.setProperty("primary", True)
        export_button.clicked.connect(self.open_export)
        toolbar.addWidget(export_button)
        self.window.addToolBar(toolbar)
        self._toolbar = toolbar

    def _build_pages(self) -> None:
        from aavc.presentation.screens.home import create_home_screen
        from aavc.presentation.screens.new_project import create_new_project_screen
        from aavc.presentation.widgets.editor_shell import create_editor_shell

        self._route_widgets[UiRoute.HOME] = create_home_screen(
            lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX),
            self.open_project,
        )
        self._route_widgets[UiRoute.NEW_PROJECT_DOCX] = create_new_project_screen(
            lambda: self.show_route(UiRoute.HOME),
            self.create_project_from_docx,
        )
        self._route_widgets[UiRoute.EDITOR] = create_editor_shell("overview").root
        self._route_widgets[UiRoute.SCENE_SINGLE] = create_editor_shell("single").root
        self._route_widgets[UiRoute.SCENE_DOUBLE] = create_editor_shell("double").root
        self._route_widgets[UiRoute.SUBTITLE_EDITOR] = create_editor_shell("subtitle").root
        self._route_widgets[UiRoute.EXPORT_SETTINGS] = create_editor_shell("subtitle").root
        self._route_widgets[UiRoute.VALIDATION_CENTER] = create_editor_shell("overview").root
        for widget in self._route_widgets.values():
            self.stack.addWidget(widget)

    def show_route(self, route: UiRoute) -> None:
        widget = self._route_widgets[route]
        self.stack.setCurrentWidget(widget)
        self.window.setProperty("ui_state", route.value)
        editor_chrome = route not in {UiRoute.HOME, UiRoute.NEW_PROJECT_DOCX}
        self.window.menuBar().setVisible(editor_chrome)
        if self._toolbar is not None:
            self._toolbar.setVisible(editor_chrome)
        if route is UiRoute.EXPORT_SETTINGS:
            self.open_export()
        elif route is UiRoute.VALIDATION_CENTER:
            self.open_validation()

    def open_export(self) -> None:
        from aavc.presentation.dialogs.export_settings import create_export_dialog

        dialog = create_export_dialog(self.window)
        dialog.setModal(True)
        dialog.show()
        self._active_dialog = dialog

    def open_validation(self) -> None:
        from aavc.presentation.dialogs.validation_center import create_validation_dialog

        dialog = create_validation_dialog(self.window)
        dialog.setModal(False)
        dialog.show()
        self._active_dialog = dialog

    def show(self) -> None:
        self.window.show()

    def resize(self, width: int, height: int) -> None:
        self.window.resize(width, height)

    def grab(self) -> Any:
        from PySide6.QtCore import QPoint, QRect
        from PySide6.QtGui import QColor, QPainter, QPixmap

        base = self.window.grab()
        dialog = self._active_dialog
        if dialog is None or not dialog.isVisible():
            return base

        dialog_grab = dialog.grab()
        result = QPixmap(base)
        painter = QPainter(result)
        route = str(self.window.property("ui_state") or "")
        if route == UiRoute.EXPORT_SETTINGS.value:
            painter.fillRect(
                QRect(0, 0, result.width(), result.height()),
                QColor(23, 32, 51, 80),
            )
            x = max(0, (result.width() - dialog_grab.width()) // 2)
            y = max(0, (result.height() - dialog_grab.height()) // 2)
        elif route == UiRoute.VALIDATION_CENTER.value:
            x = max(0, result.width() - dialog_grab.width())
            y = max(0, METRICS.menu_h + METRICS.toolbar_h)
        else:
            global_pos = dialog.mapToGlobal(QPoint(0, 0))
            window_global = self.window.mapToGlobal(QPoint(0, 0))
            x = global_pos.x() - window_global.x()
            y = global_pos.y() - window_global.y()
        painter.drawPixmap(x, y, dialog_grab)
        painter.end()
        return result

    def close(self) -> None:
        self.window.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.window, name)


def create_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> MainWindow:
    return MainWindow(services, initial_state=initial_state)
