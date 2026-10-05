from __future__ import annotations

from aavc.presentation.windows.animation_menu_window import (
    AnimationMenuMainWindow,
    animation_menu_enabled,
    auto_motion_all_enabled,
    stored_animation_seed,
)
from aavc.presentation.windows.project_menu_window import ProjectMenuMainWindow


def test_animation_menu_window_preserves_project_menu_layer() -> None:
    assert issubclass(AnimationMenuMainWindow, ProjectMenuMainWindow)


def test_selected_scene_animation_actions_require_project_and_scene() -> None:
    assert animation_menu_enabled(has_project=False, has_selected_scene=False) is False
    assert animation_menu_enabled(has_project=True, has_selected_scene=False) is False
    assert animation_menu_enabled(has_project=False, has_selected_scene=True) is False
    assert animation_menu_enabled(has_project=True, has_selected_scene=True) is True


def test_auto_motion_all_only_requires_active_project() -> None:
    assert auto_motion_all_enabled(has_project=False) is False
    assert auto_motion_all_enabled(has_project=True) is True


def test_stored_animation_seed_is_resilient_and_qt_safe() -> None:
    assert stored_animation_seed({}) == 1
    assert stored_animation_seed({"animation_seed": "12"}) == 12
    assert stored_animation_seed({"animation_seed": "not-a-number"}) == 1
    assert stored_animation_seed({"animation_seed": "999999999999"}) == 2147483647
    assert stored_animation_seed({"animation_seed": "-999999999999"}) == -2147483647
