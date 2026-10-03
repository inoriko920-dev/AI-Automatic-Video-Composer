from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from aavc.domain.project.models import ProjectState

Severity = Literal["ERROR", "WARNING"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    severity: Severity
    message: str
    scene_number: int | None = None
    asset_id: str | None = None


def validate_project(project: ProjectState) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    by_asset = {binding.asset_id: binding for binding in project.bindings}
    for scene in project.scenes:
        if scene.duration_seconds < 1.0:
            issues.append(
                ValidationIssue(
                    code="SCENE_DURATION_SHORT",
                    severity="WARNING",
                    message=f"Durasi Scene {scene.scene_number} terlalu pendek",
                    scene_number=scene.scene_number,
                )
            )
        for asset_id in scene.asset_ids:
            binding = by_asset.get(asset_id)
            if binding is None or binding.status != "READY":
                issues.append(
                    ValidationIssue(
                        code="ASSET_NOT_READY",
                        severity="ERROR",
                        message=f"{asset_id} belum READY",
                        scene_number=scene.scene_number,
                        asset_id=asset_id,
                    )
                )
    return tuple(issues)
