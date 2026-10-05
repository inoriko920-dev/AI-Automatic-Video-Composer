from __future__ import annotations

from aavc.presentation.windows.view_menu_window import view_target_requires_project


def test_project_views_require_active_project() -> None:
    assert view_target_requires_project("editor")
    assert view_target_requires_project("subtitle")
    assert view_target_requires_project("validation")


def test_home_view_does_not_require_active_project() -> None:
    assert not view_target_requires_project("home")
