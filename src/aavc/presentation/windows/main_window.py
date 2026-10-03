from __future__ import annotations

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
        self._route_widgets: dict[UiRoute, object] = {}
        self._build_menu(QAction)
        self._build_toolbar(QToolBar, QAction)
        self._build_pages()
        self.show_route(parse_route(initial_state))

    def _build_menu(self, QAction) -> None:
        menu = self.window.menuBar()
        for name in ["File", "Edit", "Proyek", "Tampilan", "Animasi", "AI", "Ekspor", "Bantuan"]:
            m = menu.addMenu(name)
            if name == "File":
                a = QAction("Proyek Baru", self.window); a.triggered.connect(lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX)); m.addAction(a)
                b = QAction("Buka Proyek", self.window); b.triggered.connect(lambda: self.show_route(UiRoute.EDITOR)); m.addAction(b)
                m.addSeparator(); m.addAction("Simpan"); m.addAction("Keluar")
            elif name == "Ekspor":
                e = QAction("Ekspor Video", self.window); e.triggered.connect(self.open_export); m.addAction(e)
            elif name == "Bantuan":
                m.addAction("Shortcut & Bantuan Cepat")
            else:
                m.addAction(f"{name} — menu")

    def _build_toolbar(self, QToolBar, QAction) -> None:
        toolbar = QToolBar("Utama", self.window); toolbar.setMovable(False); toolbar.setFixedHeight(METRICS.toolbar_h)
        for text, callback in [
            ("Proyek Baru", lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX)),
            ("Buka Proyek", lambda: self.show_route(UiRoute.EDITOR)),
            ("Simpan", lambda: None), ("Impor Media", lambda: None), ("Tambah Teks", lambda: self.show_route(UiRoute.SUBTITLE_EDITOR)),
            ("Rekam Narasi", lambda: None), ("AI", lambda: None),
        ]:
            act=QAction(text,self.window); act.triggered.connect(callback); toolbar.addAction(act)
        toolbar.addSeparator(); spacer=QAction("                                      ",self.window); spacer.setEnabled(False); toolbar.addAction(spacer)
        export=QAction("Ekspor Video",self.window); export.triggered.connect(self.open_export); toolbar.addAction(export)
        self.window.addToolBar(toolbar)

    def _build_pages(self) -> None:
        from aavc.presentation.screens.home import create_home_screen
        from aavc.presentation.screens.new_project import create_new_project_screen
        from aavc.presentation.widgets.editor_shell import create_editor_shell

        self._route_widgets[UiRoute.HOME] = create_home_screen(lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX), lambda: self.show_route(UiRoute.EDITOR))
        self._route_widgets[UiRoute.NEW_PROJECT_DOCX] = create_new_project_screen(lambda: self.show_route(UiRoute.HOME), lambda: self.show_route(UiRoute.EDITOR))
        self._route_widgets[UiRoute.EDITOR] = create_editor_shell("overview").root
        self._route_widgets[UiRoute.SCENE_SINGLE] = create_editor_shell("single").root
        self._route_widgets[UiRoute.SCENE_DOUBLE] = create_editor_shell("double").root
        self._route_widgets[UiRoute.SUBTITLE_EDITOR] = create_editor_shell("subtitle").root
        self._route_widgets[UiRoute.EXPORT_SETTINGS] = create_editor_shell("subtitle").root
        self._route_widgets[UiRoute.VALIDATION_CENTER] = create_editor_shell("overview").root
        for widget in self._route_widgets.values(): self.stack.addWidget(widget)

    def show_route(self, route: UiRoute) -> None:
        widget=self._route_widgets[route]; self.stack.setCurrentWidget(widget)
        self.window.setProperty("ui_state", route.value)
        if route is UiRoute.EXPORT_SETTINGS:
            self.open_export()
        elif route is UiRoute.VALIDATION_CENTER:
            self.open_validation()

    def open_export(self) -> None:
        from aavc.presentation.dialogs.export_settings import create_export_dialog
        dialog=create_export_dialog(self.window); dialog.setModal(True); dialog.show(); self._active_dialog=dialog

    def open_validation(self) -> None:
        from aavc.presentation.dialogs.validation_center import create_validation_dialog
        dialog=create_validation_dialog(self.window); dialog.setModal(True); dialog.show(); self._active_dialog=dialog

    def show(self) -> None: self.window.show()
    def resize(self, width: int, height: int) -> None: self.window.resize(width,height)
    def grab(self): return self.window.grab()
    def close(self) -> None: self.window.close()
    def __getattr__(self, name: str): return getattr(self.window,name)


def create_main_window(services: FoundationServices, initial_state: str = "UI-002") -> MainWindow:
    return MainWindow(services, initial_state=initial_state)
