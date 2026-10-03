from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path

from aavc.diagnostics.bundle import create_diagnostics_bundle
from aavc.diagnostics.logging import configure_file_logger, log_event
from aavc.diagnostics.redaction import redact_text, redact_value


def test_recursive_redaction_removes_nested_secrets() -> None:
    value = {
        "api_key": "AIza" + "A" * 32,
        "nested": {"token": "private-token", "note": "password=hunter2"},
        "items": ["Bearer abc.def.ghi", "safe"],
    }
    cleaned = redact_value(value)
    rendered = json.dumps(cleaned)
    assert "private-token" not in rendered
    assert "hunter2" not in rendered
    assert "abc.def.ghi" not in rendered
    assert "[REDACTED]" in rendered


def test_structured_logger_redacts_message_and_context(tmp_path: Path) -> None:
    path = tmp_path / "aavc.jsonl"
    logger = configure_file_logger(path, name="aavc-step13-test", level=logging.INFO)
    log_event(
        logger,
        logging.INFO,
        "provider.test",
        "api_key=very-secret",
        context={"authorization": "Bearer top-secret", "scene": "08"},
    )
    for handler in logger.handlers:
        handler.flush()
    raw = path.read_text(encoding="utf-8")
    assert "very-secret" not in raw
    assert "top-secret" not in raw
    assert "provider.test" in raw
    assert '"scene": "08"' in raw


def test_diagnostics_bundle_is_atomic_and_redacted(tmp_path: Path) -> None:
    source = tmp_path / "runtime.log"
    source.write_text("token=secret-value\nnormal line\n", encoding="utf-8")
    target = tmp_path / "support.zip"
    result = create_diagnostics_bundle(
        target,
        metadata={"api_key": "do-not-store", "project": "Demo"},
        log_files=[source],
    )
    assert result == target
    assert target.is_file()
    assert not target.with_suffix(".zip.tmp").exists()
    with zipfile.ZipFile(target) as archive:
        system = archive.read("system.json").decode("utf-8")
        log = archive.read("logs/runtime.log").decode("utf-8")
    assert "do-not-store" not in system
    assert "secret-value" not in log
    assert "Demo" in system
    assert "normal line" in log


def test_direct_text_redaction_handles_google_style_key() -> None:
    key = "AIza" + "B" * 32
    assert key not in redact_text(f"provider key {key}")
