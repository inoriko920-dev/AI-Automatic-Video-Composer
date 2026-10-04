from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.presentation.subtitle_view import build_subtitle_views
from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title
from aavc.subtitles import (
    SubtitleCue,
    parse_srt,
    parse_srt_timestamp,
    replace_subtitle_cue,
)


def create_subtitle_cue_edit_page(
    source: str | Path,
    *,
    on_save_copy: Callable[[tuple[SubtitleCue, ...]], None] | None = None,
) -> Any:
    from PySide6.QtWidgets import (
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    source_path = Path(source).resolve()
    cues = parse_srt(source_path)
    views = build_subtitle_views(cues)

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.addWidget(section_title("Edit Cue Subtitle — Simpan sebagai Salinan"))
    layout.addWidget(
        muted_label(
            "Edit teks dan timing cue terpilih. Source asli tidak ditimpa; tombol Simpan "
            "Salinan SRT meminta lokasi file baru lalu project diarahkan ke salinan tersebut."
        )
    )

    cue_list = QListWidget()
    for view in views:
        cue_list.addItem(QListWidgetItem(view.list_label))
    layout.addWidget(cue_list, 1)

    text = QTextEdit()
    text.setMaximumHeight(92)
    start = QLineEdit()
    start.setPlaceholderText("00:00:00,000")
    end = QLineEdit()
    end.setPlaceholderText("00:00:01,000")
    form = QFormLayout()
    form.addRow("Teks", text)
    form.addRow("Waktu Mulai (IN)", start)
    form.addRow("Waktu Selesai (OUT)", end)
    layout.addLayout(form)

    warning = QLabel("")
    warning.setStyleSheet("color:#B45309; background:#FEF3C7; padding:4px 8px;")
    warning.setVisible(False)
    layout.addWidget(warning)

    action_row = QHBoxLayout()
    save_copy = make_primary_button("Simpan Salinan SRT…")
    if on_save_copy is None:
        save_copy.setEnabled(False)
        save_copy.setToolTip("Penyimpanan salinan SRT belum terhubung ke sesi project.")
    action_row.addStretch(1)
    action_row.addWidget(save_copy)
    layout.addLayout(action_row)

    def show_selected(row: int) -> None:
        if row < 0 or row >= len(cues):
            text.clear()
            start.clear()
            end.clear()
            save_copy.setEnabled(False)
            warning.setVisible(False)
            return
        cue = cues[row]
        view = views[row]
        text.setPlainText(cue.text.replace("\\N", "\n"))
        start.setText(view.start_label.replace(".", ","))
        end.setText(view.end_label.replace(".", ","))
        warning.setText("⚠ Cue ini tumpang tindih dengan cue sebelumnya pada source saat ini.")
        warning.setVisible(view.overlaps_previous)
        save_copy.setEnabled(on_save_copy is not None)

    def save_selected_copy() -> None:
        row = cue_list.currentRow()
        try:
            edited = replace_subtitle_cue(
                cues,
                row,
                text=text.toPlainText(),
                start_seconds=parse_srt_timestamp(start.text()),
                end_seconds=parse_srt_timestamp(end.text()),
            )
        except ValueError as error:
            QMessageBox.warning(page, "Cue subtitle tidak valid", str(error))
            return
        if on_save_copy is not None:
            on_save_copy(edited)

    cue_list.currentRowChanged.connect(show_selected)
    if on_save_copy is not None:
        save_copy.clicked.connect(save_selected_copy)
    if cues:
        cue_list.setCurrentRow(0)
    else:
        layout.addWidget(muted_label("File SRT tidak memiliki cue yang dapat diedit."))
        show_selected(-1)
    return page
