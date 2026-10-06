import json

import pytest
from pathlib import Path

from aavc.application.services.vertical_slice import create_project_state
from aavc.persistence.recovery import RecoveryManager
from aavc.persistence.serializer import loads_project, save_project

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "step10"


def _project():
    return create_project_state(
        title="demo",
        scene_docx=FIXTURE / "scene_asset_demo.docx",
        asset_directory=FIXTURE / "assets",
    )


def test_old_schema_loads_into_schema_two() -> None:
    project = _project()
    payload = project.to_dict()
    payload["schema_version"] = 1
    for key in ["animations", "subtitle_style", "subtitle_animation", "render_quality"]:
        payload.pop(key, None)
    restored = loads_project(json.dumps(payload))
    assert restored.schema_version == 2
    assert restored.subtitle_style.preset_name == "Dokumenter"


def test_recovery_snapshot_roundtrip(tmp_path: Path) -> None:
    project = _project()
    project_path = save_project(project, tmp_path / "demo.aavcproj")
    manager = RecoveryManager()
    snapshot = manager.write_snapshot(project, project_path)
    assert snapshot.recovery_path.exists()
    recovered = manager.load_snapshot(project_path)
    assert recovered.title == project.title
    restored_path = manager.restore_snapshot(project_path)
    assert restored_path.exists()



def test_future_schema_is_rejected_instead_of_silently_downgraded() -> None:
    project = _project()
    payload = project.to_dict()
    payload["schema_version"] = 99

    with pytest.raises(ValueError, match="lebih baru"):
        loads_project(json.dumps(payload))
