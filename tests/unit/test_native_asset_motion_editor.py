from pathlib import Path

import pytest

from aavc.application.commands import (
    RemoveAnimationAssignment,
    SetAnimationAssignment,
)
from aavc.application.services.project_session import ProjectSession
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.project.models import AnimationAssignment
from aavc.presentation.dialogs.asset_motion import (
    NATIVE_MOTION_CHOICES,
    find_asset_motion_assignment,
)
from aavc.rendering import build_ffmpeg_command, build_render_plan

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project():
    return create_project_state(
        title="native-motion-editor",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def test_native_motion_choices_match_phase_one_contract() -> None:
    assert NATIVE_MOTION_CHOICES == ("Rise", "Pan", "Drift")


def test_find_asset_motion_assignment_is_target_specific() -> None:
    project = _project()
    scene = project.scenes[0]
    assignment = AnimationAssignment(
        scene_number=scene.scene_number,
        asset_id=scene.asset_ids[0],
        enter_effect="Rise",
        exit_effect="Drift",
        intensity=0.8,
    )

    assert (
        find_asset_motion_assignment(
            (assignment,), scene.scene_number, scene.asset_ids[0]
        )
        is assignment
    )
    assert find_asset_motion_assignment((assignment,), scene.scene_number, "A999") is None


def test_apply_remove_and_undo_native_motion_reaches_ffmpeg(tmp_path: Path) -> None:
    project = _project()
    scene = project.scenes[0]
    asset_id = scene.asset_ids[0]
    assignment = AnimationAssignment(
        scene_number=scene.scene_number,
        asset_id=asset_id,
        enter_effect="Pan",
        exit_effect="Drift",
        intensity=1.2,
    )
    session = ProjectSession()
    session.start(project, tmp_path / "native-motion.aavcproj")

    applied = session.execute(SetAnimationAssignment(assignment))
    command = build_ffmpeg_command(build_render_plan(applied, tmp_path / "animated.mp4"))
    filter_graph = command[command.index("-filter_complex") + 1]
    assert "overlay=x='" in filter_graph
    assert find_asset_motion_assignment(applied.animations, scene.scene_number, asset_id) == assignment

    removed = session.execute(RemoveAnimationAssignment(scene.scene_number, asset_id))
    assert find_asset_motion_assignment(removed.animations, scene.scene_number, asset_id) is None

    restored = session.undo()
    assert find_asset_motion_assignment(restored.animations, scene.scene_number, asset_id) == assignment


def test_remove_native_motion_rejects_missing_assignment_without_history(tmp_path: Path) -> None:
    project = _project()
    scene = project.scenes[0]
    session = ProjectSession()
    session.start(project, tmp_path / "native-motion.aavcproj")

    with pytest.raises(ValueError, match="belum ada"):
        session.execute(RemoveAnimationAssignment(scene.scene_number, scene.asset_ids[0]))

    assert not session.is_dirty
    assert not session.can_undo
