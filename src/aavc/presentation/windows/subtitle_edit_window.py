from __future__ import annotations

from pathlib import Path

from aavc.application.commands import SetSubtitleSource
from aavc.bootstrap.composition_root import FoundationServices
from aavc.domain.errors import AAVCError
from aavc.presentation.navigation import UiRoute
from aavc.presentation.windows.native_motion_preview_window import NativeMotionPreviewMainWindow
from aavc.subtitles import SubtitleCue, write_srt_atomic


class SubtitleEditMainWindow(NativeMotionPreviewMainWindow):
    """Main window with safe selected-cue editing through copied SRT sources."""

    def save_subtitle_copy(self, cues: tuple[SubtitleCue, ...]) -> None:
        from PySide6.QtWidgets import QFileDialog

        project = self.services.project_session.current
        if project is None or not project.subtitle_source:
            self._show_project_notice(
                "Subtitle tidak tersedia",
                "Project aktif belum memiliki source subtitle SRT.",
            )
            return

        source = Path(project.subtitle_source).expanduser().resolve()
        default_destination = source.with_name(f"{source.stem}.edited.srt")
        chosen, _ = QFileDialog.getSaveFileName(
            self.window,
            "Simpan Salinan Subtitle SRT",
            str(default_destination),
            "Subtitle SRT (*.srt)",
        )
        if not chosen:
            return

        destination = Path(chosen).expanduser()
        if destination.suffix.lower() != ".srt":
            destination = destination.with_suffix(".srt")
        try:
            destination_resolved = destination.resolve()
        except OSError as error:
            self._show_project_error("Lokasi subtitle tidak valid", error)
            return
        if destination_resolved == source:
            self._show_project_notice(
                "Source asli dilindungi",
                "Pilih nama atau lokasi file lain. Flow Edit Cue tidak menimpa SRT source asli.",
            )
            return

        try:
            saved = write_srt_atomic(destination_resolved, cues)
            self.services.project_session.execute(SetSubtitleSource(str(saved)))
        except (AAVCError, OSError, ValueError) as error:
            self._show_project_error("Gagal menyimpan salinan subtitle", error)
            return

        self._refresh_window_title()
        self.refresh_editor_overview()
        self.open_subtitle_editor()
        self.window.statusBar().showMessage(
            f"Salinan subtitle disimpan: {saved.name}. "
            "Project sekarang memakai source baru; klik Simpan untuk menyimpan referensi project.",
            9000,
        )

    def open_subtitle_editor(self) -> None:
        from aavc.presentation.screens.live_subtitle import create_live_subtitle_screen

        project = self.services.project_session.current
        if project is None:
            self._show_project_notice(
                "Subtitle tidak tersedia",
                "Buat atau buka proyek terlebih dahulu.",
            )
            return
        if not project.subtitle_source:
            self._show_project_notice(
                "Subtitle belum ada",
                "Impor file SRT melalui tombol Impor Media terlebih dahulu.",
            )
            return

        try:
            replacement = create_live_subtitle_screen(
                project.subtitle_source,
                style=project.subtitle_style,
                animation=project.subtitle_animation,
                on_apply_style=self.set_subtitle_style,
                on_apply_animation=self.set_subtitle_animation,
                on_reload=self.open_subtitle_editor,
                on_save_copy=self.save_subtitle_copy,
            )
        except (OSError, ValueError) as error:
            self._show_project_error("Gagal membaca subtitle", error)
            return

        self._replace_route_widget(UiRoute.SUBTITLE_EDITOR, replacement)
        self.show_route(UiRoute.SUBTITLE_EDITOR)
        self.window.statusBar().showMessage(
            f"Subtitle dimuat: {Path(project.subtitle_source).name}",
            5000,
        )


def create_subtitle_edit_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> SubtitleEditMainWindow:
    return SubtitleEditMainWindow(services, initial_state=initial_state)
