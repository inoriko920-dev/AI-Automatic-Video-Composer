from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from aavc.rendering.render_plan import RenderPlan


class PreflightSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class PreflightIssue:
    code: str
    severity: PreflightSeverity
    message: str


@dataclass(frozen=True, slots=True)
class PreflightReport:
    issues: tuple[PreflightIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity is PreflightSeverity.ERROR for issue in self.issues)

    def require_ok(self) -> None:
        if self.ok:
            return
        codes = ", ".join(issue.code for issue in self.issues if issue.severity is PreflightSeverity.ERROR)
        raise RenderPreflightError(f"render preflight failed: {codes}")


class RenderPreflightError(RuntimeError):
    pass


def inspect_render_plan(plan: RenderPlan, *, allow_overwrite: bool = False) -> PreflightReport:
    issues: list[PreflightIssue] = []
    if plan.width <= 0 or plan.height <= 0:
        issues.append(_error("invalid_dimensions", "Render dimensions must be positive."))
    if plan.fps <= 0:
        issues.append(_error("invalid_fps", "Render FPS must be positive."))
    if not plan.scenes:
        issues.append(_error("no_scenes", "Render plan contains no scenes."))

    for scene in plan.scenes:
        if scene.duration_seconds <= 0:
            issues.append(
                _error(
                    "invalid_scene_duration",
                    f"Scene {scene.scene_number} has a non-positive duration.",
                )
            )
        if not scene.asset_paths:
            issues.append(_error("scene_has_no_assets", f"Scene {scene.scene_number} has no assets."))
        for asset_path in scene.asset_paths:
            _require_readable_file(asset_path, "missing_asset", issues)

    if plan.narration_audio:
        _require_readable_file(plan.narration_audio, "missing_narration", issues)
    if plan.subtitle_ass:
        _require_readable_file(plan.subtitle_ass, "missing_subtitle", issues)

    output = Path(plan.output_path)
    if output.suffix.lower() != ".mp4":
        issues.append(_warning("unexpected_extension", "Output extension is not .mp4."))
    if output.exists() and not allow_overwrite:
        issues.append(_error("output_exists", "Output already exists and overwrite is disabled."))
    parent = output.parent if output.parent != Path("") else Path(".")
    if not parent.exists():
        issues.append(_error("output_parent_missing", "Output directory does not exist."))
    elif not parent.is_dir():
        issues.append(_error("output_parent_not_directory", "Output parent is not a directory."))
    elif not os.access(parent, os.W_OK):
        issues.append(_error("output_parent_not_writable", "Output directory is not writable."))

    if plan.duration_seconds <= 0:
        issues.append(_error("invalid_total_duration", "Total render duration must be positive."))
    return PreflightReport(tuple(issues))


def _require_readable_file(path_value: str, code: str, issues: list[PreflightIssue]) -> None:
    path = Path(path_value)
    if not path.is_file():
        issues.append(_error(code, f"Required input is missing: {path.name}"))
        return
    if not os.access(path, os.R_OK):
        issues.append(_error(f"{code}_unreadable", f"Required input is unreadable: {path.name}"))


def _error(code: str, message: str) -> PreflightIssue:
    return PreflightIssue(code, PreflightSeverity.ERROR, message)


def _warning(code: str, message: str) -> PreflightIssue:
    return PreflightIssue(code, PreflightSeverity.WARNING, message)
