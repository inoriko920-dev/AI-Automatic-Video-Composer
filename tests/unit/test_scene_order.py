from pathlib import Path

import pytest

from aavc.application.commands.scene_order import MoveScene
from aavc.application.services.project_session import ProjectSession
from aavc.application.services.vertical_slice import create_project_state
from aavc.rendering import build_render_plan

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project():
    return create_project_state(
        title="scene-order",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def _numbers(project):
    return tuple(scene.scene_number for scene in project.scenes)


def test_move_scene_updates_history_timeline_source_and_render_order(tmp_path: Path) -> None:
    project = _project()
    first, second, *_ = project.scenes
    original_order = _numbers(project)
    expected_order = (second.scene_number, first.scene_number, *original_order[2:])

    session = ProjectSession()
    session.start(project, tmp_path / "scene-order.aavcproj")

    moved = session.execute(MoveScene(second.scene_number, -1))
    assert _numbers(moved) == expected_order
    assert session.is_dirty

    render_plan = build_render_plan(moved, tmp_path / "scene-order.mp4")
    assert tuple(scene.scene_number for scene in render_plan.scenes) == expected_order

    undone = session.undo()
    assert _numbers(undone) == original_order
    assert not session.is_dirty

    redone = session.redo()
    assert _numbers(redone) == expected_order
    assert session.is_dirty


def test_move_scene_rejects_boundary_without_history_entry(tmp_path: Path) -> None:
    project = _project()
    first = project.scenes[0]
    session = ProjectSession()
    session.start(project, tmp_path / "scene-order.aavcproj")

    with pytest.raises(ValueError, match="paling atas"):
        session.execute(MoveScene(first.scene_number, -1))

    assert _numbers(session.current) == _numbers(project)
    assert not session.is_dirty
    assert not session.can_undo


def test_move_scene_requires_single_step_offset() -> None:
    project = _project()
    with pytest.raises(ValueError, match="-1 atau 1"):
        MoveScene(project.scenes[0].scene_number, 2).apply(project)
