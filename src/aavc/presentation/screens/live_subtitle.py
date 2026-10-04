from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.domain.project.models import SubtitleAnimationSettings, SubtitleStyle
from aavc.presentation.widgets.editor_shell import create_editor_shell
from aavc.presentation.widgets.live_subtitle import create_live_subtitle_inspector


def create_live_subtitle_screen(
    source: str | Path,
    *,
    style: SubtitleStyle | None = None,
    animation: SubtitleAnimationSettings | None = None,
    on_apply_style: Callable[[SubtitleStyle], None] | None = None,
    on_apply_animation: Callable[[SubtitleAnimationSettings], None] | None = None,
    on_reload: Callable[[], None] | None = None,
) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

    source_path = Path(source).resolve()
    parts = create_editor_shell("subtitle")
    inspector = create_live_subtitle_inspector(
        source_path,
        style=style,
        animation=animation,
        on_apply_style=on_apply_style,
        on_apply_animation=on_apply_animation,
        on_reload=on_reload,
    )

    parts.right_tabs.removeTab(0)
    parts.right_tabs.insertTab(0, inspector, "Subtitle")
    parts.right_tabs.setCurrentIndex(0)

    parts.left_tabs.clear()
    source_page = QWidget()
    source_layout = QVBoxLayout(source_page)
    source_layout.addWidget(QLabel("Subtitle Project Aktif"))
    source_name = QLabel(source_path.name)
    source_name.setWordWrap(True)
    source_name.setStyleSheet("font-weight:700;")
    source_layout.addWidget(source_name)
    source_note = QLabel(
        "Daftar cue, gaya, dan animasi subtitle berada pada panel kanan. Kembali ke "
        "Editor untuk memilih Scene atau melihat timeline project."
    )
    source_note.setWordWrap(True)
    source_note.setStyleSheet("color:#64748B;")
    source_layout.addWidget(source_note)
    source_layout.addStretch(1)
    parts.left_tabs.addTab(source_page, "SRT")

    parts.preview_label.clear()
    parts.preview_label.setText(
        "Preview burn-in subtitle belum tersedia.\n"
        "Gaya dan animasi yang diterapkan di panel kanan digunakan saat Ekspor Video."
    )
    parts.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parts.preview_label.setStyleSheet(
        "border:1px solid #CBD5E1; background:#F8FAFD; color:#64748B; padding:24px;"
    )
    parts.timeline.setVisible(False)
    parts.status_label.setText(
        f"Subtitle aktif: {source_path.name}   ·   Editor cue read-only   ·   "
        "Gaya + animasi subtitle render-backed"
    )
    return parts.root
