from __future__ import annotations

from typing import Any, Literal

from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.navigation import UiRoute
from aavc.presentation.windows.help_window import HelpMainWindow

ViewTarget = Literal["home", "editor", "subtitle", "validation"]


def view_target_requires_project(target: ViewTarget) -> bool:
    return target != "home"


class ViewMenuMainWindow(HelpMainWindow):
    """Replace the frozen View placeholder with safe live navigation actions."""

    def _build_menu(self, action_type: Any) -> None:
        super()._build_menu(action_type)

        view_menu: Any | None = None
        for menu_action in self.window.menuBar().actions():
            if menu_action.text() == "Tampilan":
                view_menu = menu_action.menu()
                break
        if view_menu is None:
            return

        view_menu.clear()
        actions = (
            ("Beranda", "home"),
            ("Editor Proyek", "editor"),
            ("Subtitle", "subtitle"),
            ("Validation Center", "validation"),
        )
        for label, target in actions:
            action = action_type(label, self.window)
            action.triggered.connect(
                lambda _checked=False, target_name=target: self.open_view_target(target_name)
            )
            view_menu.addAction(action)

    def open_view_target(self, target: ViewTarget) -> None:
        project = self.services.project_session.current
        if view_target_requires_project(target) and project is None:
            self._show_project_notice(
                "Tampilan belum tersedia",
                "Buat atau buka proyek terlebih dahulu.",
            )
            return

        if target == "home":
            self.show_route(UiRoute.HOME)
            return
        if target == "editor":
            self.refresh_editor_overview()
            self.show_route(UiRoute.EDITOR)
            return
        if target == "subtitle":
            self.open_subtitle_editor()
            return
        if target == "validation":
            self.show_route(UiRoute.VALIDATION_CENTER)
            return
        raise ValueError(f"Target Tampilan tidak dikenal: {target}")


def create_view_menu_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> ViewMenuMainWindow:
    return ViewMenuMainWindow(services, initial_state=initial_state)
