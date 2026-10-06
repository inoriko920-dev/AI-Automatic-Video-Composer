import json
from pathlib import Path

import pytest

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



def test_corrupt_recovery_snapshot_does_not_replace_project_or_backup(tmp_path: Path) -> None:
    project = _project()
    project_path = save_project(project, tmp_path / "demo.aavcproj")
    original_project_bytes = project_path.read_bytes()

    manager = RecoveryManager()
    recovery = manager.recovery_path_for(project_path)
    recovery.write_text("{not valid json", encoding="utf-8")

    backup = project_path.with_suffix(project_path.suffix + ".pre-recovery.bak")
    backup.write_bytes(b"existing-backup")

    with pytest.raises(ValueError):
        manager.restore_snapshot(project_path)

    assert project_path.read_bytes() == original_project_bytes
    assert backup.read_bytes() == b"existing-backup"
    assert not project_path.with_suffix(project_path.suffix + ".restore.tmp").exists()



def test_save_project_does_not_touch_legacy_fixed_temp_name(tmp_path: Path) -> None:
    destination = tmp_path / "demo.aavcproj"
    legacy_temp = destination.with_suffix(destination.suffix + ".tmp")
    legacy_temp.write_text("user-owned-temp", encoding="utf-8")

    save_project(_project(), destination)

    assert destination.is_file()
    assert legacy_temp.read_text(encoding="utf-8") == "user-owned-temp"
    assert list(tmp_path.glob(".*.aavc-save-*.tmp")) == []


def test_recovery_restore_does_not_touch_legacy_fixed_restore_temp(tmp_path: Path) -> None:
    original = _project()
    project_path = save_project(original, tmp_path / "demo.aavcproj")
    manager = RecoveryManager()

    recovered = original.to_dict()
    recovered["title"] = "recovered-title"
    manager.recovery_path_for(project_path).write_text(
        json.dumps(recovered),
        encoding="utf-8",
    )

    legacy_temp = project_path.with_suffix(project_path.suffix + ".restore.tmp")
    legacy_temp.write_text("user-owned-restore-temp", encoding="utf-8")

    manager.restore_snapshot(project_path)

    assert legacy_temp.read_text(encoding="utf-8") == "user-owned-restore-temp"
    assert list(tmp_path.glob(".*.aavc-restore-*.tmp")) == []


@pytest.mark.parametrize("payload", ["[]", "null", "1", '"text"'])
def test_project_root_must_be_json_object(payload: str) -> None:
    with pytest.raises(ValueError, match="root"):
        loads_project(payload)


def test_structurally_invalid_project_payloads_are_rejected() -> None:
    base = _project().to_dict()

    invalid_payloads: list[dict[str, object]] = []

    no_assets = json.loads(json.dumps(base))
    no_assets["scenes"][0]["asset_ids"] = []
    no_assets["scenes"][0]["source_quotes"] = []
    invalid_payloads.append(no_assets)

    three_assets = json.loads(json.dumps(base))
    three_assets["scenes"][0]["asset_ids"] = ["A001", "A002", "A003"]
    three_assets["scenes"][0]["source_quotes"] = ["one", "two", "three"]
    invalid_payloads.append(three_assets)

    duplicate_scene = json.loads(json.dumps(base))
    duplicate_scene["scenes"][1]["scene_number"] = duplicate_scene["scenes"][0]["scene_number"]
    invalid_payloads.append(duplicate_scene)

    string_duration = json.loads(json.dumps(base))
    string_duration["scenes"][0]["duration_seconds"] = "3.0"
    invalid_payloads.append(string_duration)

    negative_duration = json.loads(json.dumps(base))
    negative_duration["scenes"][0]["duration_seconds"] = -1.0
    invalid_payloads.append(negative_duration)

    infinite_duration = json.loads(json.dumps(base))
    infinite_duration["scenes"][0]["duration_seconds"] = float("inf")
    invalid_payloads.append(infinite_duration)

    missing_binding = json.loads(json.dumps(base))
    missing_binding["bindings"] = missing_binding["bindings"][1:]
    invalid_payloads.append(missing_binding)

    for payload in invalid_payloads:
        with pytest.raises(ValueError):
            loads_project(json.dumps(payload))


def test_missing_media_binding_remains_loadable_for_relink() -> None:
    payload = _project().to_dict()
    payload["bindings"][0]["path"] = "Z:/moved/A001.png"
    payload["bindings"][0]["status"] = "MISSING"

    restored = loads_project(json.dumps(payload))

    assert restored.bindings[0].status == "MISSING"
    assert restored.bindings[0].path == "Z:/moved/A001.png"


def test_structurally_invalid_recovery_preserves_project_and_existing_backup(
    tmp_path: Path,
) -> None:
    project = _project()
    project_path = save_project(project, tmp_path / "demo.aavcproj")
    original_project_bytes = project_path.read_bytes()

    manager = RecoveryManager()
    payload = project.to_dict()
    payload["scenes"][0]["asset_ids"] = []
    payload["scenes"][0]["source_quotes"] = []
    recovery = manager.recovery_path_for(project_path)
    recovery.write_text(json.dumps(payload), encoding="utf-8")

    backup = project_path.with_suffix(project_path.suffix + ".pre-recovery.bak")
    backup.write_bytes(b"existing-backup")

    with pytest.raises(ValueError, match="asset_ids"):
        manager.restore_snapshot(project_path)

    assert project_path.read_bytes() == original_project_bytes
    assert backup.read_bytes() == b"existing-backup"
    assert list(tmp_path.glob(".*.aavc-restore-*.tmp")) == []
