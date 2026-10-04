from __future__ import annotations

from dataclasses import dataclass, replace

from aavc.domain.project.models import ProjectState


@dataclass(frozen=True, slots=True)
class MoveScene:
    """Move one stable scene number by one position in project order."""

    scene_number: int
    offset: int

    def apply(self, project: ProjectState) -> ProjectState:
        if self.offset not in {-1, 1}:
            raise ValueError("Offset perpindahan Scene harus -1 atau 1")

        index = next(
            (
                current_index
                for current_index, scene in enumerate(project.scenes)
                if scene.scene_number == self.scene_number
            ),
            None,
        )
        if index is None:
            raise ValueError(f"Scene {self.scene_number} tidak ditemukan")

        target = index + self.offset
        if target < 0:
            raise ValueError("Scene sudah berada di posisi paling atas")
        if target >= len(project.scenes):
            raise ValueError("Scene sudah berada di posisi paling bawah")

        scenes = list(project.scenes)
        scenes[index], scenes[target] = scenes[target], scenes[index]
        return replace(project, scenes=tuple(scenes))

    def describe(self) -> str:
        direction = "atas" if self.offset < 0 else "bawah"
        return f"Pindah Scene {self.scene_number} ke {direction}"


@dataclass(frozen=True, slots=True)
class DeleteScene:
    """Delete one scene while preserving a renderable project."""

    scene_number: int

    def apply(self, project: ProjectState) -> ProjectState:
        if len(project.scenes) <= 1:
            raise ValueError("Scene terakhir tidak boleh dihapus")

        if not any(scene.scene_number == self.scene_number for scene in project.scenes):
            raise ValueError(f"Scene {self.scene_number} tidak ditemukan")

        scenes = tuple(
            scene for scene in project.scenes if scene.scene_number != self.scene_number
        )
        used_asset_ids = {
            asset_id
            for scene in scenes
            for asset_id in scene.asset_ids
        }
        bindings = tuple(
            binding for binding in project.bindings if binding.asset_id in used_asset_ids
        )
        animations = tuple(
            assignment
            for assignment in project.animations
            if assignment.scene_number != self.scene_number
        )
        return replace(
            project,
            scenes=scenes,
            bindings=bindings,
            animations=animations,
        )

    def describe(self) -> str:
        return f"Hapus Scene {self.scene_number}"


@dataclass(frozen=True, slots=True)
class DuplicateScene:
    """Duplicate one scene immediately after its source with a new stable number."""

    scene_number: int

    def apply(self, project: ProjectState) -> ProjectState:
        source_index = next(
            (
                index
                for index, scene in enumerate(project.scenes)
                if scene.scene_number == self.scene_number
            ),
            None,
        )
        if source_index is None:
            raise ValueError(f"Scene {self.scene_number} tidak ditemukan")

        new_scene_number = max(scene.scene_number for scene in project.scenes) + 1
        source_scene = project.scenes[source_index]
        duplicate = replace(source_scene, scene_number=new_scene_number)

        scenes = list(project.scenes)
        scenes.insert(source_index + 1, duplicate)

        cloned_animations = tuple(
            replace(assignment, scene_number=new_scene_number)
            for assignment in project.animations
            if assignment.scene_number == self.scene_number
        )
        return replace(
            project,
            scenes=tuple(scenes),
            animations=(*project.animations, *cloned_animations),
        )

    def describe(self) -> str:
        return f"Duplikasi Scene {self.scene_number}"
