from __future__ import annotations

from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.windows.subtitle_export_guard_window import (
    SubtitleExportGuardMainWindow,
)


def subtitle_project_save_requires_working_copy_guard(
    *,
    editor_active: bool,
    working_copy_dirty: bool,
) -> bool:
    """Return whether project save must stop before local subtitle cue edits are lost."""

    return editor_active and working_copy_dirty


class SubtitleSaveGuardMainWindow(SubtitleExportGuardMainWindow):
    """Prevent project save from implying dirty subtitle cue edits were persisted."""

    def save_project(self) -> None:
        if subtitle_project_save_requires_working_copy_guard(
            editor_active=self._subtitle_editor_is_active(),
            working_copy_dirty=self._subtitle_working_copy_dirty,
        ):
            self._show_project_notice(
                "Subtitle belum disimpan",
                "Working copy subtitle memiliki perubahan cue yang belum disimpan ke file SRT. "
                "Gunakan Simpan Salinan di Subtitle Editor terlebih dahulu, lalu simpan project.",
            )
            return

        super().save_project()


def create_subtitle_save_guard_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> SubtitleSaveGuardMainWindow:
    return SubtitleSaveGuardMainWindow(services, initial_state=initial_state)
