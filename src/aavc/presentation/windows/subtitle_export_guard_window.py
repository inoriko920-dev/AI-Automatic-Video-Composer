from __future__ import annotations

from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.windows.subtitle_import_guard_window import (
    SubtitleImportGuardMainWindow,
)


def subtitle_export_requires_working_copy_guard(
    *,
    editor_active: bool,
    working_copy_dirty: bool,
) -> bool:
    """Return whether export must resolve local subtitle cue edits first."""

    return editor_active and working_copy_dirty


class SubtitleExportGuardMainWindow(SubtitleImportGuardMainWindow):
    """Prevent render from silently using an older on-disk subtitle source."""

    def open_export(self) -> None:
        if subtitle_export_requires_working_copy_guard(
            editor_active=self._subtitle_editor_is_active(),
            working_copy_dirty=self._subtitle_working_copy_dirty,
        ):
            if not self._confirm_subtitle_working_copy_discard("mengekspor video"):
                return
            self._rebuild_subtitle_editor_after_discard_authorized()
            if self._subtitle_working_copy_dirty:
                # Rebuild failed (for example the backing SRT disappeared). Do not
                # continue to export while the visible cue working copy is unresolved.
                return

        super().open_export()


def create_subtitle_export_guard_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> SubtitleExportGuardMainWindow:
    return SubtitleExportGuardMainWindow(services, initial_state=initial_state)
