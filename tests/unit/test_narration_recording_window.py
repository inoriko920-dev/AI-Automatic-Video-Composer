from __future__ import annotations

from pathlib import Path

from aavc.presentation.windows.narration_recording_window import (
    NarrationRecordingMainWindow,
    default_narration_recording_path,
    ensure_wav_suffix,
    narration_recording_enabled,
)
from aavc.presentation.windows.project_action_state_window import (
    ProjectActionStateMainWindow,
)


def test_narration_recording_runtime_preserves_project_action_state_layer() -> None:
    assert issubclass(NarrationRecordingMainWindow, ProjectActionStateMainWindow)


def test_narration_recording_requires_active_project() -> None:
    assert narration_recording_enabled(has_project=False) is False
    assert narration_recording_enabled(has_project=True) is True


def test_ensure_wav_suffix_normalizes_destination(tmp_path: Path) -> None:
    expected = (tmp_path / "take.wav").resolve()
    assert ensure_wav_suffix(tmp_path / "take") == expected
    assert ensure_wav_suffix(tmp_path / "take.MP3") == expected
    assert ensure_wav_suffix(tmp_path / "take.WAV") == expected


def test_default_recording_path_prefers_project_directory(tmp_path: Path) -> None:
    project_dir = tmp_path / "project-dir"
    source_dir = tmp_path / "source-dir"
    project_dir.mkdir()
    source_dir.mkdir()

    result = default_narration_recording_path(
        project_path=project_dir / "sample.aavcproj",
        source_docx=source_dir / "scene.docx",
        project_title="My Project 01",
    )

    assert result == project_dir / "My_Project_01_narration.wav"


def test_default_recording_path_falls_back_to_docx_directory(tmp_path: Path) -> None:
    source_dir = tmp_path / "source-dir"
    source_dir.mkdir()

    result = default_narration_recording_path(
        project_path=None,
        source_docx=source_dir / "scene.docx",
        project_title="  ",
    )

    assert result == source_dir / "project_narration.wav"
