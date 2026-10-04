from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.presentation.subtitle_view import SubtitleCueView, build_subtitle_views
from aavc.presentation.widgets.common import muted_label, section_title
from aavc.subtitles import parse_srt


def load_subtitle_views(source: str | Path) -> tuple[SubtitleCueView, ...]:
    return build_subtitle_views(parse_srt(source))


def create_live_subtitle_inspector(
    source: str | Path,
    *,
    on_reload: Callable[[], None] | None = None,
) -> Any:
    from PySide6.QtWidgets import (
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    source_path = Path(source).resolve()
    views = load_subtitle_views(source_path)

    tabs = QTabWidget()
    text_page = QWidget()
    layout = QVBoxLayout(text_page)

    header = QHBoxLayout()
    header.addWidget(section_title(f"Daftar Subtitle ({len(views)} cue)"))
    header.addStretch(1)
    add_button = QPushButton("＋ Tambah Cue")
    add_button.setEnabled(False)
    add_button.setToolTip("Penulisan ulang SRT belum diaktifkan pada build ini.")
    header.addWidget(add_button)
    layout.addLayout(header)
    layout.addWidget(muted_label(f"Sumber: {source_path.name}"))

    cue_list = QListWidget()
    for view in views:
        cue_list.addItem(QListWidgetItem(view.list_label))
    layout.addWidget(cue_list, 1)

    edit_header = QHBoxLayout()
    edit_header.addWidget(section_title("Detail Cue"))
    edit_header.addStretch(1)
    warning = QLabel("")
    warning.setStyleSheet("color:#B45309; background:#FEF3C7; padding:4px 8px;")
    warning.setVisible(False)
    edit_header.addWidget(warning)
    layout.addLayout(edit_header)

    text = QTextEdit()
    text.setMaximumHeight(74)
    text.setReadOnly(True)
    layout.addWidget(text)

    start = QLineEdit()
    start.setReadOnly(True)
    end = QLineEdit()
    end.setReadOnly(True)
    form = QFormLayout()
    form.addRow("Waktu Mulai (IN)", start)
    form.addRow("Waktu Selesai (OUT)", end)
    layout.addLayout(form)

    row = QHBoxLayout()
    split_button = QPushButton("Pisah Cue")
    split_button.setEnabled(False)
    split_button.setToolTip("Penulisan ulang SRT belum diaktifkan pada build ini.")
    merge_button = QPushButton("Gabung")
    merge_button.setEnabled(False)
    merge_button.setToolTip("Penulisan ulang SRT belum diaktifkan pada build ini.")
    reload_button = QPushButton("Muat Ulang SRT")
    if on_reload is None:
        reload_button.setEnabled(False)
    else:
        reload_button.clicked.connect(on_reload)
    row.addWidget(split_button)
    row.addWidget(merge_button)
    row.addWidget(reload_button)
    layout.addLayout(row)

    def show_selected(row_index: int) -> None:
        if row_index < 0 or row_index >= len(views):
            text.clear()
            start.clear()
            end.clear()
            warning.setVisible(False)
            return
        view = views[row_index]
        text.setPlainText(view.text.replace("\\N", "\n"))
        start.setText(view.start_label)
        end.setText(view.end_label)
        warning.setText("⚠ Tumpang tindih dengan cue sebelumnya")
        warning.setVisible(view.overlaps_previous)

    cue_list.currentRowChanged.connect(show_selected)
    if views:
        cue_list.setCurrentRow(0)
    else:
        layout.addWidget(muted_label("File SRT tidak memiliki cue yang dapat dibaca."))
        show_selected(-1)

    tabs.addTab(text_page, "Teks")

    style_page = QWidget()
    style_layout = QVBoxLayout(style_page)
    style_layout.addWidget(
        muted_label(
            "Gaya subtitle project digunakan saat render. Editor gaya interaktif belum "
            "terhubung pada layar ini."
        )
    )
    style_layout.addStretch(1)
    tabs.addTab(style_page, "Gaya")

    animation_page = QWidget()
    animation_layout = QVBoxLayout(animation_page)
    animation_layout.addWidget(
        muted_label(
            "Animasi subtitle project digunakan saat kompilasi ASS. Editor animasi "
            "interaktif belum terhubung pada layar ini."
        )
    )
    animation_layout.addStretch(1)
    tabs.addTab(animation_page, "Animasi")
    return tabs
