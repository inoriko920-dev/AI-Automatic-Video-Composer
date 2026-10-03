from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aavc.platform.process_runner import ProcessRunner


@dataclass(frozen=True, slots=True)
class RenderOutputReport:
    exists: bool
    non_empty: bool
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    duration_seconds: float | None = None
    issues: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.exists and self.non_empty and not self.issues


def validate_render_output(
    output_path: str | Path,
    *,
    expected_width: int | None = None,
    expected_height: int | None = None,
    expected_fps: float | None = None,
    expected_duration_seconds: float | None = None,
    ffprobe_path: str | Path | None = None,
    process_runner: ProcessRunner | None = None,
    duration_tolerance_seconds: float = 0.25,
) -> RenderOutputReport:
    path = Path(output_path)
    if not path.is_file():
        return RenderOutputReport(False, False, issues=("output_missing",))
    if path.stat().st_size <= 0:
        return RenderOutputReport(True, False, issues=("output_empty",))
    if ffprobe_path is None:
        return RenderOutputReport(True, True)

    runner = process_runner or ProcessRunner()
    result = runner.run(
        [
            str(ffprobe_path),
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ],
        timeout_seconds=30.0,
    )
    if result.returncode != 0:
        return RenderOutputReport(True, True, issues=("ffprobe_failed",))
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return RenderOutputReport(True, True, issues=("ffprobe_invalid_json",))
    if not isinstance(payload, dict):
        return RenderOutputReport(True, True, issues=("ffprobe_invalid_payload",))

    width, height, fps = _video_properties(payload)
    duration = _duration(payload)
    issues: list[str] = []
    if expected_width is not None and width != expected_width:
        issues.append("width_mismatch")
    if expected_height is not None and height != expected_height:
        issues.append("height_mismatch")
    if expected_fps is not None and (fps is None or abs(fps - expected_fps) > 0.02):
        issues.append("fps_mismatch")
    if expected_duration_seconds is not None and (
        duration is None or abs(duration - expected_duration_seconds) > duration_tolerance_seconds
    ):
        issues.append("duration_mismatch")
    return RenderOutputReport(
        True,
        True,
        width=width,
        height=height,
        fps=fps,
        duration_seconds=duration,
        issues=tuple(issues),
    )


def _video_properties(payload: dict[str, Any]) -> tuple[int | None, int | None, float | None]:
    streams = payload.get("streams")
    if not isinstance(streams, list):
        return None, None, None
    for stream in streams:
        if not isinstance(stream, dict) or stream.get("codec_type") != "video":
            continue
        width = stream.get("width")
        height = stream.get("height")
        raw_rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
        return (
            width if isinstance(width, int) else None,
            height if isinstance(height, int) else None,
            _parse_rate(raw_rate),
        )
    return None, None, None


def _duration(payload: dict[str, Any]) -> float | None:
    format_value = payload.get("format")
    if isinstance(format_value, dict):
        parsed = _parse_float(format_value.get("duration"))
        if parsed is not None:
            return parsed
    streams = payload.get("streams")
    if isinstance(streams, list):
        for stream in streams:
            if isinstance(stream, dict):
                parsed = _parse_float(stream.get("duration"))
                if parsed is not None:
                    return parsed
    return None


def _parse_float(value: object) -> float | None:
    if isinstance(value, (str, int, float)):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _parse_rate(value: object) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            den = float(denominator)
            return float(numerator) / den if den else None
        except ValueError:
            return None
    return _parse_float(value)
