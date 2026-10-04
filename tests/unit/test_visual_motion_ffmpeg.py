from dataclasses import replace
from pathlib import Path

from aavc.animation.compiler import compile_motion_overlay_position
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.project.models import AnimationAssignment
from aavc.rendering import build_ffmpeg_command, build_render_plan, validate_render_plan

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project():
    return create_project_state(
        title="visual-motion",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def test_motion_compiler_combines_enter_and_exit_axes() -> None:
    assignment = AnimationAssignment(
        scene_number=1,
        asset_id="A001",
        enter_effect="Rise",
        exit_effect="Pan",
        intensity=0.5,
    )

    x_expr, y_expr = compile_motion_overlay_position(
        base_x="(W-w)/2",
        base_y="(H-h)/2",
        assignment=assignment,
        duration_seconds=3.0,
    )

    assert x_expr == (
        "((W-w)/2)+(if(gt(t,2.750000),"
        "((t-2.750000)/0.250000)*W*0.030000,0))"
    )
    assert y_expr == (
        "((H-h)/2)+(if(lt(t,0.250000),"
        "(1-t/0.250000)*H*0.040000,0))"
    )


def test_project_without_assignment_keeps_original_overlay_command(tmp_path: Path) -> None:
    plan = build_render_plan(_project(), tmp_path / "out.mp4")
    command = " ".join(build_ffmpeg_command(plan))

    assert "overlay=x=(W-w)/2:y=(H-h)/2:shortest=1" in command
    assert "overlay=x='" not in command


def test_double_scene_partial_motion_changes_only_assigned_overlay(tmp_path: Path) -> None:
    project = _project()
    scene = next(item for item in project.scenes if len(item.asset_ids) == 2)
    assignment = AnimationAssignment(
        scene_number=scene.scene_number,
        asset_id=scene.asset_ids[1],
        enter_effect="Pan",
        exit_effect="Drift",
        intensity=1.0,
    )
    project = replace(project, animations=(assignment,))

    command = " ".join(
        build_ffmpeg_command(build_render_plan(project, tmp_path / "out.mp4"))
    )

    assert "overlay=x=W/2-w-12:y=(H-h)/2:shortest=1" in command
    assert "overlay=x='(W/2+12)+" in command
    assert "W*0.060000" in command
    assert "if(gt(t,2.750000)" in command


def test_unsupported_effect_keeps_default_motion_and_warns(tmp_path: Path) -> None:
    project = _project()
    scene = project.scenes[0]
    baseline = " ".join(
        build_ffmpeg_command(build_render_plan(project, tmp_path / "out.mp4"))
    )
    assignment = AnimationAssignment(
        scene_number=scene.scene_number,
        asset_id=scene.asset_ids[0],
        enter_effect="Pop",
        exit_effect="Stomp",
        intensity=1.0,
    )
    project = replace(project, animations=(assignment,))
    plan = build_render_plan(project, tmp_path / "out.mp4")

    assert " ".join(build_ffmpeg_command(plan)) == baseline
    report = validate_render_plan(plan)
    fallback_messages = [
        issue.message
        for issue in report.issues
        if issue.code == "VISUAL_EFFECT_FALLBACK"
    ]
    assert any("Pop" in message for message in fallback_messages)
    assert any("Stomp" in message for message in fallback_messages)
    assert report.ok


def test_preflight_rejects_nonempty_animation_slot_mismatch(tmp_path: Path) -> None:
    project = _project()
    plan = build_render_plan(project, tmp_path / "out.mp4")
    scene = plan.scenes[0]
    fake = AnimationAssignment(
        scene_number=scene.scene_number,
        asset_id="A999",
        enter_effect="Rise",
        exit_effect="Pan",
    )
    broken_scene = replace(scene, animations=(fake, fake))
    broken = replace(plan, scenes=(broken_scene, *plan.scenes[1:]))

    report = validate_render_plan(broken)

    assert any(issue.code == "ANIMATION_SLOT_MISMATCH" for issue in report.issues)
    assert not report.ok
