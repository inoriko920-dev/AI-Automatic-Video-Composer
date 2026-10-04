from __future__ import annotations

from dataclasses import dataclass, replace

from aavc.domain.project.models import ProjectState


@dataclass(frozen=True, slots=True)
class RemoveAnimationAssignment:
    """Remove one asset animation assignment through project history."""

    scene_number: int
    asset_id: str

    def apply(self, project: ProjectState) -> ProjectState:
        valid_targets = {
            (scene.scene_number, asset_id)
            for scene in project.scenes
            for asset_id in scene.asset_ids
        }
        key = (self.scene_number, self.asset_id)
        if key not in valid_targets:
            raise ValueError("Target animasi tidak ada di scene")
        if not any(
            (item.scene_number, item.asset_id) == key
            for item in project.animations
        ):
            raise ValueError("Assignment animasi belum ada pada aset ini")

        animations = tuple(
            item
            for item in project.animations
            if (item.scene_number, item.asset_id) != key
        )
        return replace(project, animations=animations)

    def describe(self) -> str:
        return f"Hapus animasi {self.asset_id} pada Scene {self.scene_number}"
