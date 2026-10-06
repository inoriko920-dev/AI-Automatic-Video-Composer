from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

import pytest

from aavc.application.services.export_service import ExportOptions, render_project
from aavc.application.services.selection_export_service import render_project_selection
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.errors import RenderError
from aavc.domain.project.models import AnimationAssignment, ProjectState
from aavc.platform.process_runner import (
    WINDOWS_COMMAND_LINE_LIMIT,
    ProcessResult,
    ProcessRunner,
    windows_command_line_units,
)
from aavc.rendering import build_ffmpeg_command, build_render_plan

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


class FakeRunner(ProcessRunner):
    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self.filter_graphs: list[str] = []

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        del timeout_seconds
        command = list(argv)
        self.commands.append(command)
        if "-filter_complex_script" in command:
            graph_path = Path(command[command.index("-filter_complex_script") + 1])
            self.filter_graphs.append(graph_path.read_text(encoding="utf-8"))
        Path(command[-1]).write_bytes(b"fake-mp4")
        return ProcessResult(0, "", "")


class FailingRunner(ProcessRunner):
    def run(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        del timeout_seconds
        command = list(argv)
        Path(command[-1]).write_bytes(b"partial-output")
        return ProcessResult(1, "", "ffmpeg failed")


def _project() -> ProjectState:
    return create_project_state(
        title="export-demo",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def test_render_project_maps_options_into_ffmpeg_command(tmp_path: Path) -> None:
    output = tmp_path / "video.mp4"
    runner = FakeRunner()
    options = ExportOptions(
        output_path=str(output),
        video_codec="libx265",
        encoder_preset="slow",
        crf=20,
        width=1280,
        height=720,
        fps=60,
        sharpen_amount=0.10,
        burn_subtitles=False,
    )

    result = render_project(_project(), options, ffmpeg="fake-ffmpeg", runner=runner)

    assert result.output_path == str(output.resolve())
    assert output.read_bytes() == b"fake-mp4"
    command = runner.commands[0]
    assert command[0] == "fake-ffmpeg"
    assert command[command.index("-c:v") + 1] == "libx265"
    assert command[command.index("-preset") + 1] == "slow"
    assert command[command.index("-crf") + 1] == "20"
    assert command[command.index("-r") + 1] == "60"
    assert "-filter_complex" not in command
    assert "-filter_complex_script" in command
    assert "s=1280x720" in runner.filter_graphs[0]
    graph_path = Path(command[command.index("-filter_complex_script") + 1])
    assert not graph_path.exists()


def test_render_project_uses_temporary_subtitle_ass_without_clobbering_sidecar(
    tmp_path: Path,
) -> None:
    subtitle = tmp_path / "subtitle.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo dunia\n",
        encoding="utf-8",
    )
    project = replace(_project(), subtitle_source=str(subtitle))
    output = tmp_path / "with-subtitle.mp4"
    user_sidecar = output.with_suffix(".subtitle.ass")
    user_sidecar.write_text("user-owned", encoding="utf-8")
    runner = FakeRunner()

    render_project(
        project,
        ExportOptions(output_path=str(output), burn_subtitles=True),
        ffmpeg="fake-ffmpeg",
        runner=runner,
    )

    filters = runner.filter_graphs[0]
    assert "ass=filename=" in filters
    assert ".aavc-subtitle-" in filters
    assert user_sidecar.read_text(encoding="utf-8") == "user-owned"
    assert list(tmp_path.glob(".*.aavc-subtitle-*.ass")) == []


def test_render_project_cleans_subtitle_staging_when_ffmpeg_fails(tmp_path: Path) -> None:
    subtitle = tmp_path / "subtitle.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo dunia\n",
        encoding="utf-8",
    )
    project = replace(_project(), subtitle_source=str(subtitle))
    output = tmp_path / "failed.mp4"
    user_sidecar = output.with_suffix(".subtitle.ass")
    user_sidecar.write_text("keep-me", encoding="utf-8")

    with pytest.raises(RenderError, match="ffmpeg failed"):
        render_project(
            project,
            ExportOptions(output_path=str(output), burn_subtitles=True),
            ffmpeg="fake-ffmpeg",
            runner=FailingRunner(),
        )

    assert user_sidecar.read_text(encoding="utf-8") == "keep-me"
    assert list(tmp_path.glob(".*.aavc-subtitle-*.ass")) == []


def test_selection_export_also_cleans_subtitle_staging(tmp_path: Path) -> None:
    subtitle = tmp_path / "subtitle.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo dunia\n",
        encoding="utf-8",
    )
    project = replace(_project(), subtitle_source=str(subtitle))
    output = tmp_path / "selection.mp4"
    user_sidecar = output.with_suffix(".subtitle.ass")
    user_sidecar.write_text("selection-user-owned", encoding="utf-8")
    runner = FakeRunner()

    render_project_selection(
        project,
        ExportOptions(output_path=str(output), burn_subtitles=True),
        start_seconds=0.0,
        end_seconds=1.0,
        ffmpeg="fake-ffmpeg",
        runner=runner,
    )

    filters = runner.filter_graphs[0]
    assert ".aavc-subtitle-" in filters
    assert user_sidecar.read_text(encoding="utf-8") == "selection-user-owned"
    assert list(tmp_path.glob(".*.aavc-subtitle-*.ass")) == []


def test_render_project_stops_on_preflight_error(tmp_path: Path) -> None:
    runner = FakeRunner()
    options = ExportOptions(output_path=str(tmp_path / "bad.mp4"), width=0)

    with pytest.raises(RenderError, match="Resolusi render tidak valid"):
        render_project(_project(), options, ffmpeg="fake-ffmpeg", runner=runner)

    assert runner.commands == []



def test_large_filter_graph_is_removed_from_windows_command_line(tmp_path: Path) -> None:
    base = _project()
    source_scene = base.scenes[0]
    asset_id = source_scene.asset_ids[0]
    scenes = tuple(
        replace(source_scene, scene_number=index + 1)
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
    output = tmp_path / "large.mp4"

    inline = build_ffmpeg_command(build_render_plan(project, output), ffmpeg="fake-ffmpeg")
    assert windows_command_line_units(inline) > WINDOWS_COMMAND_LINE_LIMIT

    runner = FakeRunner()
    render_project(
        project,
        ExportOptions(output_path=str(output), burn_subtitles=False),
        ffmpeg="fake-ffmpeg",
        runner=runner,
    )

    executed = runner.commands[0]
    assert "-filter_complex_script" in executed
    assert "-filter_complex" not in executed
    assert windows_command_line_units(executed) < WINDOWS_COMMAND_LINE_LIMIT
    assert len(runner.filter_graphs[0]) > 20_000
    assert list(tmp_path.glob(".*.aavc-filter-*.txt")) == []


def test_subtitle_filter_path_escapes_apostrophe_and_filtergraph_delimiters(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "Toni's video,[draft]"
    output_dir.mkdir()
    subtitle = tmp_path / "subtitle.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo dunia\n",
        encoding="utf-8",
    )
    project = replace(_project(), subtitle_source=str(subtitle))
    runner = FakeRunner()

    render_project(
        project,
        ExportOptions(output_path=str(output_dir / "video.mp4"), burn_subtitles=True),
        ffmpeg="fake-ffmpeg",
        runner=runner,
    )

    graph = runner.filter_graphs[0]
    assert "ass=filename=" in graph
    assert "Toni" in graph
    assert "\\\'" in graph
    assert "\\," in graph
    assert "\\[" in graph
    assert "\\]" in graph
    assert list(output_dir.glob(".*.aavc-subtitle-*.ass")) == []
    assert list(output_dir.glob(".*.aavc-filter-*.txt")) == []
