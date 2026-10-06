from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from aavc.domain.project.models import (
    AnimationAssignment,
    AssetBinding,
    ProjectState,
    RenderQualitySettings,
    Scene,
    SubtitleAnimationSettings,
    SubtitleStyle,
)

CURRENT_SCHEMA_VERSION = 2


def dumps_project(project: ProjectState) -> str:
    return json.dumps(project.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def loads_project(text: str) -> ProjectState:
    data = json.loads(text)
    source_schema_version = int(data.get("schema_version", 1))
    if source_schema_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            "Versi project tidak didukung: "
            f"schema {source_schema_version} lebih baru dari schema "
            f"{CURRENT_SCHEMA_VERSION} yang didukung aplikasi ini"
        )
    return ProjectState(
        schema_version=CURRENT_SCHEMA_VERSION,
        title=data["title"],
        source_docx=data["source_docx"],
        asset_directory=data["asset_directory"],
        scenes=tuple(
            Scene(
                scene_number=int(scene["scene_number"]),
                asset_ids=tuple(scene["asset_ids"]),
                source_quotes=tuple(scene["source_quotes"]),
                duration_seconds=float(scene.get("duration_seconds", 3.0)),
            )
            for scene in data["scenes"]
        ),
        bindings=tuple(AssetBinding(**binding) for binding in data["bindings"]),
        narration_audio=data.get("narration_audio"),
        subtitle_source=data.get("subtitle_source"),
        background_source=data.get("background_source"),
        fps=int(data.get("fps", 30)),
        width=int(data.get("width", 1920)),
        height=int(data.get("height", 1080)),
        animations=tuple(
            AnimationAssignment(**item) for item in data.get("animations", [])
        ),
        subtitle_style=SubtitleStyle(**data.get("subtitle_style", {})),
        subtitle_animation=SubtitleAnimationSettings(**data.get("subtitle_animation", {})),
        render_quality=RenderQualitySettings(**data.get("render_quality", {})),
        metadata=dict(data.get("metadata", {})),
    )


def temporary_sibling_path(path: str | Path, *, label: str) -> Path:
    destination = Path(path)
    return destination.with_name(
        f".{destination.name}.aavc-{label}-{uuid4().hex}.tmp"
    )


def save_project(project: ProjectState, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = temporary_sibling_path(destination, label="save")
    try:
        temporary.write_text(dumps_project(project), encoding="utf-8")
        temporary.replace(destination)
        return destination
    finally:
        temporary.unlink(missing_ok=True)


def load_project(path: str | Path) -> ProjectState:
    return loads_project(Path(path).read_text(encoding="utf-8"))
