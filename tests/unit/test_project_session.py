from pathlib import Path

import pytest

from aavc.application.commands import SetSceneDuration
from aavc.application.services.project_session import ProjectSession
from aavc.application.services.vertical_slice import create_project_state
from aavc.domain.project.models import ProjectState

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project() -> ProjectState:
    return create_project_state(
        title="demo-session",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def test_session_start_save_and_reopen(tmp_path: Path) -> None:
    destination = tmp_path / "demo.aavcproj"
    session = ProjectSession()
    session.start(_project(), destination)

    saved = session.save()
    assert saved == destination.resolve()
    assert destination.is_file()

    reopened = ProjectSession()
    project = reopened.open(destination)
    assert project.title == "demo-session"
    assert reopened.current == project
    assert reopened.path == destination.resolve()


def test_session_execute_undo_redo_uses_project_history() -> None:
    session = ProjectSession()
    session.start(_project())

    changed = session.execute(SetSceneDuration(1, 4.5))
    assert changed.scenes[0].duration_seconds == 4.5
    assert session.can_undo

    undone = session.undo()
    assert undone.scenes[0].duration_seconds == 3.0
    assert session.can_redo

    redone = session.redo()
    assert redone.scenes[0].duration_seconds == 4.5


def test_failed_open_preserves_existing_session(tmp_path: Path) -> None:
    destination = tmp_path / "good.aavcproj"
    session = ProjectSession()
    session.start(_project(), destination)
    session.save()
    session.open(destination)
    previous_project = session.current
    previous_path = session.path

    broken = tmp_path / "broken.aavcproj"
    broken.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError):
        session.open(broken)

    assert session.current == previous_project
    assert session.path == previous_path


def test_save_requires_active_project() -> None:
    session = ProjectSession()
    with pytest.raises(ValueError, match="Tidak ada proyek aktif"):
        session.save()
