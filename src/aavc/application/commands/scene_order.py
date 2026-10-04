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
