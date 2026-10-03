from dataclasses import replace
from pathlib import Path

from aavc.application.services.validation import validate_project
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.project.models import AssetBinding, RenderQualitySettings
from aavc.rendering import build_ffmpeg_command, build_render_plan

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project():
    return create_project_state(
        title="demo",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
        narration_audio=FIXTURE / "narration.wav",
    )


def test_validation_reports_missing_asset() -> None:
    project = _project()
    broken = tuple(
        AssetBinding(item.asset_id, item.source_quote, None, "MISSING") if item.asset_id == "A001" else item
        for item in project.bindings
    )
    issues = validate_project(replace(project, bindings=broken))
    assert any(issue.code == "ASSET_NOT_READY" and issue.asset_id == "A001" for issue in issues)


def test_documentary_crisp_settings_reach_ffmpeg_command(tmp_path: Path) -> None:
    project = replace(
        _project(),
        render_quality=RenderQualitySettings(
            preset_name="Documentary Crisp",
            video_codec="libx264",
            encoder_preset="slow",
            crf=17,
            audio_bitrate_kbps=320,
            scale_algorithm="lanczos",
            sharpen_amount=0.18,
        ),
    )
    plan = build_render_plan(project, tmp_path / "out.mp4")
    cmd = build_ffmpeg_command(plan)
    joined = " ".join(cmd)
    assert "flags=lanczos" in joined
    assert "unsharp=5:5:" in joined
    assert "-preset slow" in joined
    assert "-crf 17" in joined
    assert "-b:a 320k" in joined
