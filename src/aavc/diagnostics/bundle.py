from __future__ import annotations

import json
import platform
import sys
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from aavc.diagnostics.redaction import redact_text, redact_value


def create_diagnostics_bundle(
    output_zip: str | Path,
    *,
    metadata: Mapping[str, Any] | None = None,
    log_files: Sequence[str | Path] = (),
    text_files: Sequence[str | Path] = (),
) -> Path:
    target = Path(output_zip)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    if temp.exists():
        temp.unlink()

    system_info: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "metadata": {} if metadata is None else redact_value(dict(metadata)),
    }

    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "system.json",
            json.dumps(system_info, ensure_ascii=False, indent=2, sort_keys=True),
        )
        _add_redacted_files(archive, log_files, prefix="logs")
        _add_redacted_files(archive, text_files, prefix="text")

    temp.replace(target)
    return target


def _add_redacted_files(
    archive: zipfile.ZipFile,
    files: Sequence[str | Path],
    *,
    prefix: str,
) -> None:
    used_names: set[str] = set()
    for index, source_value in enumerate(files, start=1):
        source = Path(source_value)
        if not source.is_file():
            continue
        safe_name = _unique_name(source.name, used_names, index=index)
        raw = source.read_text(encoding="utf-8", errors="replace")
        archive.writestr(f"{prefix}/{safe_name}", redact_text(raw))


def _unique_name(name: str, used: set[str], *, index: int) -> str:
    candidate = Path(name).name or f"file-{index}.txt"
    if candidate not in used:
        used.add(candidate)
        return candidate
    path = Path(candidate)
    stem = path.stem or "file"
    suffix = path.suffix
    counter = 2
    while True:
        candidate = f"{stem}-{counter}{suffix}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        counter += 1
