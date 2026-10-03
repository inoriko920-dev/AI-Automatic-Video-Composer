from __future__ import annotations

import json
from pathlib import Path

from aavc.domain.layout import Placement
from aavc.domain.project.models import RenderQualitySettings
from aavc.platform.process_runner import ProcessResult, ProcessRunner
from aavc.rendering.preflight import PreflightSeverity, inspect_render_plan
from aavc.rendering.render_plan import RenderPlan, SceneRenderPlan
from aavc.rendering.validation import validate_render_output


def _plan(tmp_path: Path, asset: Path, output: Path) -> RenderPlan:
    scene = SceneRenderPlan(
        scene_number=1,
        duration_seconds=3.0,
        asset_paths=(str(asset),),
        placements=(Placement("A001", 0.5, 0.47, 0.72, 0.84),),
    )
    return RenderPlan(
        width=1920,
        height=1080,
        fps=30,
        scenes=(scene,),
        narration_audio=None,
        subtitle_ass=None,
        output_path=str(output),
        quality=RenderQualitySettings(),
    )


def test_render_preflight_accepts_ready_plan(tmp_path: Path) -> None:
    asset = tmp_path / "A001.png"
    asset.write_bytes(b"png-fixture")
    report = inspect_render_plan(_plan(tmp_path, asset, tmp_path / "result.mp4"))
    assert report.ok
    assert report.issues == ()


def test_render_preflight_blocks_missing_asset_and_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "result.mp4"
    output.write_bytes(b"existing")
    report = inspect_render_plan(_plan(tmp_path, tmp_path / "missing.png", output))
    codes = {issue.code for issue in report.issues if issue.severity is PreflightSeverity.ERROR}
    assert "missing_asset" in codes
    assert "output_exists" in codes
    assert not report.ok


class FakeProbeRunner(ProcessRunner):
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def run(
        self,
        argv: list[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        del argv, timeout_seconds
        return ProcessResult(0, json.dumps(self.payload), "")


def test_render_output_validation_checks_probe_properties(tmp_path: Path) -> None:
    output = tmp_path / "result.mp4"
    output.write_bytes(b"video")
    runner = FakeProbeRunner(
        {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30/1",
                }
            ],
            "format": {"duration": "6.000"},
        }
    )
    report = validate_render_output(
        output,
        expected_width=1920,
        expected_height=1080,
        expected_fps=30,
        expected_duration_seconds=6.0,
        ffprobe_path="ffprobe",
        process_runner=runner,
    )
    assert report.ok
    assert report.fps == 30.0
    assert report.duration_seconds == 6.0


def test_render_output_validation_detects_mismatch(tmp_path: Path) -> None:
    output = tmp_path / "result.mp4"
    output.write_bytes(b"video")
    runner = FakeProbeRunner(
        {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1280,
                    "height": 720,
                    "avg_frame_rate": "25/1",
                }
            ],
            "format": {"duration": "5.0"},
        }
    )
    report = validate_render_output(
        output,
        expected_width=1920,
        expected_height=1080,
        expected_fps=30,
        expected_duration_seconds=6.0,
        ffprobe_path="ffprobe",
        process_runner=runner,
    )
    assert not report.ok
    assert set(report.issues) == {
        "width_mismatch",
        "height_mismatch",
        "fps_mismatch",
        "duration_mismatch",
    }
