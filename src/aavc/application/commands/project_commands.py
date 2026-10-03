from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from aavc.animation.registry import validate_effect
from aavc.domain.project.models import AnimationAssignment, AssetBinding, ProjectState, Scene


class ProjectCommand(Protocol):
    def apply(self, project: ProjectState) -> ProjectState: ...

    def describe(self) -> str: ...


@dataclass(frozen=True, slots=True)
class SetSceneDuration:
    scene_number: int
    duration_seconds: float

    def apply(self, project: ProjectState) -> ProjectState:
        if self.duration_seconds <= 0:
            raise ValueError("Durasi scene harus lebih dari 0")
        found = False
        scenes: list[Scene] = []
        for scene in project.scenes:
            if scene.scene_number == self.scene_number:
                found = True
                scenes.append(replace(scene, duration_seconds=self.duration_seconds))
            else:
                scenes.append(scene)
        if not found:
            raise ValueError(f"Scene {self.scene_number} tidak ditemukan")
        return replace(project, scenes=tuple(scenes))

    def describe(self) -> str:
        return f"Ubah durasi Scene {self.scene_number} menjadi {self.duration_seconds:.3f}s"


@dataclass(frozen=True, slots=True)
class RelinkAsset:
    asset_id: str
    replacement_path: str

    def apply(self, project: ProjectState) -> ProjectState:
        path = Path(self.replacement_path)
        if not path.is_file():
            raise ValueError(f"File pengganti tidak ditemukan: {path}")
        found = False
        bindings: list[AssetBinding] = []
        for binding in project.bindings:
            if binding.asset_id == self.asset_id:
                found = True
                bindings.append(replace(binding, path=str(path.resolve()), status="READY"))
            else:
                bindings.append(binding)
        if not found:
            raise ValueError(f"Asset {self.asset_id} tidak ditemukan")
        return replace(project, bindings=tuple(bindings))

    def describe(self) -> str:
        return f"Relink {self.asset_id}"


@dataclass(frozen=True, slots=True)
class SetAnimationAssignment:
    assignment: AnimationAssignment

    def apply(self, project: ProjectState) -> ProjectState:
        validate_effect(self.assignment.enter_effect)
        validate_effect(self.assignment.exit_effect)
        valid_assets = {
            (scene.scene_number, asset_id)
            for scene in project.scenes
            for asset_id in scene.asset_ids
        }
        key = (self.assignment.scene_number, self.assignment.asset_id)
        if key not in valid_assets:
            raise ValueError("Target animasi tidak ada di scene")
        items = [
            item
            for item in project.animations
            if (item.scene_number, item.asset_id) != key
        ]
        items.append(self.assignment)
        items.sort(key=lambda item: (item.scene_number, item.asset_id))
        return replace(project, animations=tuple(items))

    def describe(self) -> str:
        return f"Atur animasi {self.assignment.asset_id} pada Scene {self.assignment.scene_number}"
