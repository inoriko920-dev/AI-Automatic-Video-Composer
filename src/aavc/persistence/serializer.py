from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any
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
_VALID_ASSET_STATUSES = {"READY", "MISSING", "CORRUPT", "DUPLICATE"}


def dumps_project(project: ProjectState) -> str:
    return json.dumps(project.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def _fail(field: str, message: str) -> None:
    raise ValueError(f"Project tidak valid pada {field}: {message}")


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(field, "harus object JSON")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(field, "harus array JSON")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        _fail(field, "harus string")
    return value


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _string(value, field)


def _integer(value: Any, field: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(field, "harus integer")
    if positive and value <= 0:
        _fail(field, "harus lebih dari 0")
    return value


def _number(
    value: Any,
    field: str,
    *,
    positive: bool = False,
    non_negative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(field, "harus angka")
    result = float(value)
    if not math.isfinite(result):
        _fail(field, "harus finite")
    if positive and result <= 0:
        _fail(field, "harus lebih dari 0")
    if non_negative and result < 0:
        _fail(field, "tidak boleh negatif")
    return result


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        _fail(field, "harus boolean")
    return value


def _validate_settings_objects(data: dict[str, Any]) -> None:
    for name in ("subtitle_style", "subtitle_animation", "render_quality", "metadata"):
        if name in data:
            _object(data[name], name)

    subtitle_style = _object(data.get("subtitle_style", {}), "subtitle_style")
    for key in ("preset_name", "font_family", "fill_color", "outline_color"):
        if key in subtitle_style:
            _string(subtitle_style[key], f"subtitle_style.{key}")
    for key in ("outline_width", "shadow"):
        if key in subtitle_style:
            _number(subtitle_style[key], f"subtitle_style.{key}", non_negative=True)
    for key in ("font_size", "background_opacity", "alignment", "margin_v"):
        if key in subtitle_style:
            _integer(subtitle_style[key], f"subtitle_style.{key}")
    if "background_box" in subtitle_style:
        _bool(subtitle_style["background_box"], "subtitle_style.background_box")

    subtitle_animation = _object(
        data.get("subtitle_animation", {}),
        "subtitle_animation",
    )
    for key in ("preset", "highlight_color"):
        if key in subtitle_animation:
            _string(subtitle_animation[key], f"subtitle_animation.{key}")
    for key in ("enter_duration_ms", "exit_duration_ms"):
        if key in subtitle_animation:
            value = _integer(subtitle_animation[key], f"subtitle_animation.{key}")
            if value < 0:
                _fail(f"subtitle_animation.{key}", "tidak boleh negatif")
    if "intensity" in subtitle_animation:
        _number(
            subtitle_animation["intensity"],
            "subtitle_animation.intensity",
            non_negative=True,
        )

    render_quality = _object(data.get("render_quality", {}), "render_quality")
    for key in ("preset_name", "video_codec", "encoder_preset", "scale_algorithm"):
        if key in render_quality:
            _string(render_quality[key], f"render_quality.{key}")
    for key in ("crf", "audio_bitrate_kbps"):
        if key in render_quality:
            _integer(render_quality[key], f"render_quality.{key}")
    if "sharpen_amount" in render_quality:
        _number(
            render_quality["sharpen_amount"],
            "render_quality.sharpen_amount",
            non_negative=True,
        )

    metadata = _object(data.get("metadata", {}), "metadata")
    for key, value in metadata.items():
        if not isinstance(key, str) or not isinstance(value, str):
            _fail("metadata", "key dan value harus string")


def loads_project(text: str) -> ProjectState:
    data = _object(json.loads(text), "root")

    raw_schema_version = data.get("schema_version", 1)
    source_schema_version = _integer(raw_schema_version, "schema_version", positive=True)
    if source_schema_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            "Versi project tidak didukung: "
            f"schema {source_schema_version} lebih baru dari schema "
            f"{CURRENT_SCHEMA_VERSION} yang didukung aplikasi ini"
        )

    title = _string(data.get("title"), "title")
    source_docx = _string(data.get("source_docx"), "source_docx")
    asset_directory = _string(data.get("asset_directory"), "asset_directory")

    width = _integer(data.get("width", 1920), "width", positive=True)
    height = _integer(data.get("height", 1080), "height", positive=True)
    fps = _integer(data.get("fps", 30), "fps", positive=True)

    raw_scenes = _array(data.get("scenes"), "scenes")
    if not raw_scenes:
        _fail("scenes", "minimal harus berisi satu scene")

    scenes: list[Scene] = []
    scene_numbers: set[int] = set()
    quote_by_asset: dict[str, str] = {}
    scene_asset_ids: set[str] = set()
    for index, raw_scene in enumerate(raw_scenes):
        field = f"scenes[{index}]"
        scene_data = _object(raw_scene, field)
        scene_number = _integer(
            scene_data.get("scene_number"),
            f"{field}.scene_number",
            positive=True,
        )
        if scene_number in scene_numbers:
            _fail(f"{field}.scene_number", f"duplikat Scene {scene_number}")
        scene_numbers.add(scene_number)

        raw_asset_ids = _array(scene_data.get("asset_ids"), f"{field}.asset_ids")
        if len(raw_asset_ids) not in {1, 2}:
            _fail(f"{field}.asset_ids", "harus berisi tepat 1 atau 2 aset")
        asset_ids = tuple(
            _string(value, f"{field}.asset_ids[{asset_index}]")
            for asset_index, value in enumerate(raw_asset_ids)
        )
        if len(set(asset_ids)) != len(asset_ids):
            _fail(f"{field}.asset_ids", "asset dalam satu scene tidak boleh duplikat")

        raw_quotes = _array(scene_data.get("source_quotes"), f"{field}.source_quotes")
        if len(raw_quotes) != len(asset_ids):
            _fail(
                f"{field}.source_quotes",
                "jumlah quote harus sama dengan jumlah asset_ids",
            )
        source_quotes = tuple(
            _string(value, f"{field}.source_quotes[{quote_index}]")
            for quote_index, value in enumerate(raw_quotes)
        )

        duration_seconds = _number(
            scene_data.get("duration_seconds", 3.0),
            f"{field}.duration_seconds",
            positive=True,
        )

        for asset_id, quote in zip(asset_ids, source_quotes, strict=True):
            existing_quote = quote_by_asset.get(asset_id)
            if existing_quote is not None and existing_quote != quote:
                _fail(
                    f"{field}.source_quotes",
                    f"quote untuk {asset_id} tidak konsisten antar scene",
                )
            quote_by_asset[asset_id] = quote
            scene_asset_ids.add(asset_id)

        scenes.append(
            Scene(
                scene_number=scene_number,
                asset_ids=asset_ids,
                source_quotes=source_quotes,
                duration_seconds=duration_seconds,
            )
        )

    raw_bindings = _array(data.get("bindings"), "bindings")
    bindings: list[AssetBinding] = []
    binding_ids: set[str] = set()
    for index, raw_binding in enumerate(raw_bindings):
        field = f"bindings[{index}]"
        binding_data = _object(raw_binding, field)
        asset_id = _string(binding_data.get("asset_id"), f"{field}.asset_id")
        if asset_id in binding_ids:
            _fail(f"{field}.asset_id", f"binding duplikat untuk {asset_id}")
        binding_ids.add(asset_id)

        source_quote = _string(binding_data.get("source_quote"), f"{field}.source_quote")
        path = _optional_string(binding_data.get("path"), f"{field}.path")
        status = _string(binding_data.get("status"), f"{field}.status")
        if status not in _VALID_ASSET_STATUSES:
            _fail(f"{field}.status", f"status tidak dikenal: {status}")
        if status == "READY" and path is None:
            _fail(f"{field}.path", "binding READY harus memiliki path")

        expected_quote = quote_by_asset.get(asset_id)
        if expected_quote is None:
            _fail(f"{field}.asset_id", f"{asset_id} tidak dipakai oleh scene mana pun")
        if source_quote != expected_quote:
            _fail(
                f"{field}.source_quote",
                f"quote binding {asset_id} tidak sama dengan quote scene",
            )

        bindings.append(
            AssetBinding(
                asset_id=asset_id,
                source_quote=source_quote,
                path=path,
                status=status,  # type: ignore[arg-type]
            )
        )

    missing_bindings = sorted(scene_asset_ids - binding_ids)
    if missing_bindings:
        _fail("bindings", f"binding tidak ditemukan untuk: {', '.join(missing_bindings)}")

    raw_animations = _array(data.get("animations", []), "animations")
    animations: list[AnimationAssignment] = []
    animation_targets: set[tuple[int, str]] = set()
    valid_targets = {
        (scene.scene_number, asset_id)
        for scene in scenes
        for asset_id in scene.asset_ids
    }
    for index, raw_animation in enumerate(raw_animations):
        field = f"animations[{index}]"
        animation_data = _object(raw_animation, field)
        scene_number = _integer(
            animation_data.get("scene_number"),
            f"{field}.scene_number",
            positive=True,
        )
        asset_id = _string(animation_data.get("asset_id"), f"{field}.asset_id")
        target = (scene_number, asset_id)
        if target not in valid_targets:
            _fail(field, f"target Scene {scene_number} / {asset_id} tidak ada")
        if target in animation_targets:
            _fail(field, f"assignment duplikat untuk Scene {scene_number} / {asset_id}")
        animation_targets.add(target)

        enter_effect = _string(
            animation_data.get("enter_effect", "Fade"),
            f"{field}.enter_effect",
        )
        exit_effect = _string(
            animation_data.get("exit_effect", "Fade"),
            f"{field}.exit_effect",
        )
        intensity = _number(
            animation_data.get("intensity", 1.0),
            f"{field}.intensity",
            non_negative=True,
        )
        locked = _bool(animation_data.get("locked", False), f"{field}.locked")
        animations.append(
            AnimationAssignment(
                scene_number=scene_number,
                asset_id=asset_id,
                enter_effect=enter_effect,
                exit_effect=exit_effect,
                intensity=intensity,
                locked=locked,
            )
        )

    _validate_settings_objects(data)

    narration_audio = _optional_string(data.get("narration_audio"), "narration_audio")
    subtitle_source = _optional_string(data.get("subtitle_source"), "subtitle_source")
    background_source = _optional_string(data.get("background_source"), "background_source")

    try:
        return ProjectState(
            schema_version=CURRENT_SCHEMA_VERSION,
            title=title,
            source_docx=source_docx,
            asset_directory=asset_directory,
            scenes=tuple(scenes),
            bindings=tuple(bindings),
            narration_audio=narration_audio,
            subtitle_source=subtitle_source,
            background_source=background_source,
            fps=fps,
            width=width,
            height=height,
            animations=tuple(animations),
            subtitle_style=SubtitleStyle(**data.get("subtitle_style", {})),
            subtitle_animation=SubtitleAnimationSettings(
                **data.get("subtitle_animation", {})
            ),
            render_quality=RenderQualitySettings(**data.get("render_quality", {})),
            metadata=dict(data.get("metadata", {})),
        )
    except TypeError as exc:
        raise ValueError(f"Project tidak valid: {exc}") from exc


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
