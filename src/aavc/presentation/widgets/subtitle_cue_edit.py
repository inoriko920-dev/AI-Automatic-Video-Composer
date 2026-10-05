from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.presentation.subtitle_view import build_subtitle_views
from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title
from aavc.subtitles import (
    SubtitleCue,
    delete_subtitle_cue,
    format_srt_timestamp,
    insert_subtitle_cue,
    merge_subtitle_cues,
    parse_srt,
    parse_srt_timestamp,
    replace_subtitle_cue,
    split_subtitle_cue,
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
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    source_path = Path(source).resolve()
    working_cues = parse_srt(source_path)

    page = QWidget()
    layout = QVBoxLayout(page)
    title = section_title(f"Edit Cue Subtitle ({len(working_cues)} cue) — Simpan sebagai Salinan")
    layout.addWidget(title)
    layout.addWidget(
        muted_label(
            "Edit teks/timing, tambah, pisah, gabungkan, atau hapus cue pada working copy. Source asli "
            "tidak ditimpa; Simpan Salinan SRT menulis file baru lalu project diarahkan ke salinan."
        )
    )

    cue_list = QListWidget()
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
    add_cue = QPushButton("＋ Tambah Cue Setelah Ini")
    split_cue = QPushButton("✂ Pisah Cue di Kursor")
    merge_cue = QPushButton("⇄ Gabung dengan Cue Berikutnya")
    delete_cue = QPushButton("🗑 Hapus Cue")
    save_copy = make_primary_button("Simpan Salinan SRT…")
    if on_save_copy is None:
        save_copy.setEnabled(False)
        save_copy.setToolTip("Penyimpanan salinan SRT belum terhubung ke sesi project.")
    action_row.addWidget(add_cue)
    action_row.addWidget(split_cue)
    action_row.addWidget(merge_cue)
    action_row.addWidget(delete_cue)
    action_row.addStretch(1)
    action_row.addWidget(save_copy)
    layout.addLayout(action_row)

    def views() -> tuple[Any, ...]:
        return build_subtitle_views(working_cues)

    def refresh_list(selected_row: int | None = None) -> None:
        current_views = views()
        cue_list.blockSignals(True)
        cue_list.clear()
        for view in current_views:
            cue_list.addItem(QListWidgetItem(view.list_label))
        cue_list.blockSignals(False)
        title.setText(
            f"Edit Cue Subtitle ({len(working_cues)} cue) — Simpan sebagai Salinan"
        )
        if working_cues:
            target = selected_row if selected_row is not None else 0
            cue_list.setCurrentRow(max(0, min(target, len(working_cues) - 1)))
        else:
            cue_list.setCurrentRow(-1)

    def show_selected(row: int) -> None:
        current_views = views()
        available = 0 <= row < len(working_cues)
        split_cue.setEnabled(available)
        merge_cue.setEnabled(0 <= row < len(working_cues) - 1)
        can_delete = available and len(working_cues) > 1
        delete_cue.setEnabled(can_delete)
        delete_cue.setToolTip(
            "Hapus cue terpilih dari working copy."
            if can_delete
            else "Cue terakhir tidak dapat dihapus dari working copy."
        )
        if not available:
            text.clear()
            start.clear()
            end.clear()
            save_copy.setEnabled(False)
            warning.setVisible(False)
            return
        cue = working_cues[row]
        view = current_views[row]
        text.setPlainText(cue.text.replace("\\N", "\n"))
        start.setText(format_srt_timestamp(cue.start_seconds))
        end.setText(format_srt_timestamp(cue.end_seconds))
        warning.setText("⚠ Cue ini tumpang tindih dengan cue sebelumnya pada working copy.")
        warning.setVisible(view.overlaps_previous)
        save_copy.setEnabled(on_save_copy is not None)

    def apply_current_form() -> bool:
        nonlocal working_cues
        row = cue_list.currentRow()
        if row < 0 or row >= len(working_cues):
            return False
        try:
            working_cues = replace_subtitle_cue(
                working_cues,
                row,
                text=text.toPlainText(),
                start_seconds=parse_srt_timestamp(start.text()),
                end_seconds=parse_srt_timestamp(end.text()),
            )
        except ValueError as error:
            QMessageBox.warning(page, "Cue subtitle tidak valid", str(error))
            return False
        return True

    def add_new_cue() -> None:
        nonlocal working_cues
        row = cue_list.currentRow()
        if 0 <= row < len(working_cues) and not apply_current_form():
            return
        after_row = row if 0 <= row < len(working_cues) else len(working_cues) - 1
        start_seconds = working_cues[after_row].end_seconds if after_row >= 0 else 0.0
        working_cues = insert_subtitle_cue(
            working_cues,
            after_row,
            text="Teks subtitle baru",
            start_seconds=start_seconds,
            end_seconds=start_seconds + 1.0,
        )
        refresh_list(after_row + 1)
        text.setFocus()
        text.selectAll()

    def split_current_cue() -> None:
        nonlocal working_cues
        row = cue_list.currentRow()
        cursor_position = text.textCursor().position()
        if not apply_current_form():
            return
        try:
            working_cues = split_subtitle_cue(
                working_cues,
                row,
                text_offset=cursor_position,
            )
        except ValueError as error:
            QMessageBox.warning(page, "Cue tidak dapat dipisah", str(error))
            return
        refresh_list(row + 1)

    def merge_with_next_cue() -> None:
        nonlocal working_cues
        row = cue_list.currentRow()
        if not apply_current_form():
            return
        try:
            working_cues = merge_subtitle_cues(working_cues, row)
        except ValueError as error:
            QMessageBox.warning(page, "Cue tidak dapat digabung", str(error))
            return
        refresh_list(row)

    def delete_current_cue() -> None:
        nonlocal working_cues
        row = cue_list.currentRow()
        if row < 0 or row >= len(working_cues):
            return
        cue = working_cues[row]
        answer = QMessageBox.question(
            page,
            "Hapus Cue",
            f"Hapus cue {cue.index} dari working copy?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            working_cues = delete_subtitle_cue(working_cues, row)
        except ValueError as error:
            QMessageBox.warning(page, "Cue tidak dapat dihapus", str(error))
            return
        refresh_list(min(row, len(working_cues) - 1))

    def save_selected_copy() -> None:
        if not apply_current_form():
            return
        row = cue_list.currentRow()
        refresh_list(row)
        if on_save_copy is not None:
            on_save_copy(working_cues)

    cue_list.currentRowChanged.connect(show_selected)
    add_cue.clicked.connect(add_new_cue)
    split_cue.clicked.connect(split_current_cue)
    merge_cue.clicked.connect(merge_with_next_cue)
    delete_cue.clicked.connect(delete_current_cue)
    if on_save_copy is not None:
        save_copy.clicked.connect(save_selected_copy)
    refresh_list(0 if working_cues else None)
    if not working_cues:
        layout.addWidget(
            muted_label(
                "Source SRT kosong. Gunakan Tambah Cue untuk membuat cue pertama pada working copy."
            )
        )
        show_selected(-1)
    return page