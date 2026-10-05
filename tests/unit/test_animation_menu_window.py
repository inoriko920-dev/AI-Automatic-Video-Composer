from __future__ import annotations

from aavc.presentation.windows.animation_menu_window import (
    AnimationMenuMainWindow,
    animation_menu_enabled,
)
from aavc.presentation.windows.project_menu_window import ProjectMenuMainWindow


def test_animation_menu_window_preserves_project_menu_layer() -> None:
    assert issubclass(AnimationMenuMainWindow, ProjectMenuMainWindow)


def test_animation_menu_requires_project_and_selected_scene() -> None:
    assert animation_menu_enabled(has_project=False, has_selected_scene=False) is False
    assert animation_menu_enabled(has_project=True, has_selected_scene=False) is False
    assert animation_menu_enabled(has_project=False, has_selected_scene=True) is False
    assert animation_menu_enabled(has_project=True, has_selected_scene=True) is True
