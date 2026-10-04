from dataclasses import replace
from pathlib import Path
from collections.abc import Sequence

import pytest

from aavc.application.services.export_service import ExportOptions, render_project
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.errors import RenderError
from aavc.domain.project.models import ProjectState
from aavc.platform.process_runner import ProcessResult, ProcessRunner

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


class FakeRunner(ProcessRunner):
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> ProcessResult:
        del timeout_seconds
        command = list(argv)
        self.commands.append(command)
        Path(command[-1]).write_bytes(b"fake-mp4")
        return ProcessResult(0, "", "")


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
    assert "s=1280x720" in command[command.index("-filter_complex") + 1]


def test_render_project_compiles_subtitle_only_when_enabled(tmp_path: Path) -> None:
    subtitle = tmp_path / "subtitle.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo dunia\n",
        encoding="utf-8",
    )
    project = replace(_project(), subtitle_source=str(subtitle))
    output = tmp_path / "with-subtitle.mp4"
    runner = FakeRunner()

    render_project(
        project,
        ExportOptions(output_path=str(output), burn_subtitles=True),
        ffmpeg="fake-ffmpeg",
        runner=runner,
    )

    ass = output.with_suffix(".subtitle.ass")
    assert ass.is_file()
    filters = runner.commands[0][runner.commands[0].index("-filter_complex") + 1]
    assert "ass='" in filters


def test_render_project_stops_on_preflight_error(tmp_path: Path) -> None:
    runner = FakeRunner()
    options = ExportOptions(output_path=str(tmp_path / "bad.mp4"), width=0)

    with pytest.raises(RenderError, match="Resolusi render tidak valid"):
        render_project(_project(), options, ffmpeg="fake-ffmpeg", runner=runner)

    assert runner.commands == []
