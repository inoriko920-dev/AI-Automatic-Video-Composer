from __future__ import annotations

from typing import Any

from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.design_tokens import METRICS, app_stylesheet
from aavc.presentation.navigation import UiRoute, parse_route


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
                open_action.triggered.connect(lambda: self.show_route(UiRoute.EDITOR))
                menu.addAction(open_action)
                menu.addSeparator()
                menu.addAction("Simpan")
                menu.addAction("Keluar")
            elif name == "Ekspor":
                export_action = action_type("Ekspor Video", self.window)
                export_action.triggered.connect(self.open_export)
                menu.addAction(export_action)
            elif name == "Bantuan":
                menu.addAction("Shortcut & Bantuan Cepat")
            else:
                menu.addAction(f"{name} — menu")

    def _build_toolbar(self, toolbar_type: Any, action_type: Any) -> None:
        toolbar = toolbar_type("Utama", self.window)
        toolbar.setMovable(False)
        toolbar.setFixedHeight(METRICS.toolbar_h)
        actions = [
            ("Proyek Baru", lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX)),
            ("Buka Proyek", lambda: self.show_route(UiRoute.EDITOR)),
            ("Simpan", lambda: None),
            ("Impor Media", lambda: None),
            ("Tambah Teks", lambda: self.show_route(UiRoute.SUBTITLE_EDITOR)),
            ("Rekam Narasi", lambda: None),
            ("AI Otomatis", lambda: None),
        ]
        for text, callback in actions:
            action = action_type(text, self.window)
            action.triggered.connect(callback)
            toolbar.addAction(action)
        toolbar.addSeparator()
        spacer = action_type("                                      ", self.window)
        spacer.setEnabled(False)
        toolbar.addAction(spacer)
        export_action = action_type("Ekspor Video", self.window)
        export_action.triggered.connect(self.open_export)
        toolbar.addAction(export_action)
        self.window.addToolBar(toolbar)
        self._toolbar = toolbar

    def _build_pages(self) -> None:
        from aavc.presentation.screens.home import create_home_screen
        from aavc.presentation.screens.new_project import create_new_project_screen
        from aavc.presentation.widgets.editor_shell import create_editor_shell

        self._route_widgets[UiRoute.HOME] = create_home_screen(
            lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX),
            lambda: self.show_route(UiRoute.EDITOR),
        )
        self._route_widgets[UiRoute.NEW_PROJECT_DOCX] = create_new_project_screen(
            lambda: self.show_route(UiRoute.HOME),
            lambda: self.show_route(UiRoute.EDITOR),
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
            painter.fillRect(QRect(0, 0, result.width(), result.height()), QColor(23, 32, 51, 80))
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
