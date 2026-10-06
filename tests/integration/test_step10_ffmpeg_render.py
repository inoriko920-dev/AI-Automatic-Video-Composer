import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from aavc.application.services.export_service import ExportOptions, render_project
from aavc.application.services.vertical_slice import create_project_state, run_vertical_slice
from aavc.domain.project.models import AnimationAssignment

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


@pytest.mark.integration
def test_ffmpeg_vertical_slice_renders(tmp_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg not available")
    result = run_vertical_slice(
        title="Integration Demo",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
        narration_audio=FIXTURE / "narration.wav",
        subtitle_srt=FIXTURE / "subtitle.srt",
        output_directory=tmp_path,
        ffmpeg=ffmpeg,
    )
    video = Path(result["video"])
    assert video.exists()
    assert video.stat().st_size > 10_000



@pytest.mark.integration
@pytest.mark.parametrize(
    "folder_name",
    ["folder normal", "Toni's video", "video_日本語"],
)
def test_ffmpeg_subtitle_export_supports_legal_special_paths(
    tmp_path: Path,
    folder_name: str,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg not available")

    output_dir = tmp_path / folder_name
    output_dir.mkdir()
    project = create_project_state(
        title="Subtitle Path Demo",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
        subtitle_srt=FIXTURE / "subtitle.srt",
    )
    output = output_dir / "render.mp4"

    result = render_project(
        project,
        ExportOptions(
            output_path=str(output),
            width=320,
            height=180,
            fps=24,
            burn_subtitles=True,
        ),
        ffmpeg=ffmpeg,
    )

    rendered = Path(result.output_path)
    assert rendered == output.resolve()
    assert rendered.exists()
    assert rendered.stat().st_size > 1_000
    assert list(output_dir.glob(".*.aavc-subtitle-*.ass")) == []
    assert list(output_dir.glob(".*.aavc-filter-*.txt")) == []



@pytest.mark.integration
def test_windows_large_animated_project_renders_without_oversized_argv(
    tmp_path: Path,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg not available")

    base = create_project_state(
        title="Large Windows Render",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )
    source = base.scenes[0]
    asset_id = source.asset_ids[0]
    scenes = tuple(
        replace(source, scene_number=index + 1, duration_seconds=0.1)
        for index in range(100)
    )
    animations = tuple(
        AnimationAssignment(
            scene_number=index + 1,
            asset_id=asset_id,
            enter_effect="Rise",
            exit_effect="Drift",
            intensity=1.0,
        )
        for index in range(100)
    )
    project = replace(base, scenes=scenes, animations=animations)
    output_dir = tmp_path / "100 scene Windows 測試"
    output_dir.mkdir()
    output = output_dir / "render.mp4"

    result = render_project(
        project,
        ExportOptions(
            output_path=str(output),
            width=160,
            height=90,
            fps=10,
            burn_subtitles=False,
        ),
        ffmpeg=ffmpeg,
    )

    rendered = Path(result.output_path)
    assert rendered == output.resolve()
    assert rendered.exists()
    assert rendered.stat().st_size > 1_000
    assert list(output_dir.glob(".*.aavc-filter-*.txt")) == []
