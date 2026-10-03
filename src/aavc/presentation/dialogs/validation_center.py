from __future__ import annotations

from typing import Any

from aavc.presentation.widgets.common import make_primary_button, muted_label


def create_validation_dialog(parent: Any = None) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    dialog = QDialog(parent)
    dialog.setWindowTitle("Pusat Error / Validasi")
    dialog.resize(650, 900)
    dialog.setMinimumWidth(600)
    dialog.setStyleSheet(
        "QDialog {background:#FFFFFF; border-left:1px solid #CBD5E1;} "
        "QTabWidget::pane {border:none; border-top:1px solid #E2E8F0;}"
    )

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 16, 20, 18)
    layout.setSpacing(14)

    title_row = QHBoxLayout()
    panel_title = QLabel("Pusat Error / Validasi")
    panel_title.setStyleSheet("font-size:20px; font-weight:750;")
    close_button = QPushButton("×")
    close_button.setMaximumWidth(36)
    close_button.clicked.connect(dialog.close)
    close_button.setStyleSheet("border:none; font-size:20px;")
    title_row.addWidget(panel_title)
    title_row.addStretch(1)
    title_row.addWidget(close_button)
    layout.addLayout(title_row)

    summary = QFrame()
    summary.setStyleSheet("background:#FFF7F7; border:1px solid #FECACA; border-radius:9px;")
    summary_layout = QHBoxLayout(summary)
    summary_layout.setContentsMargins(14, 12, 14, 12)
    error_icon = QLabel("!")
    error_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    error_icon.setFixedSize(38, 38)
    error_icon.setStyleSheet(
        "background:#DC2626; color:white; border-radius:19px; font-size:22px; font-weight:800;"
    )
    summary_text = QVBoxLayout()
    summary_title = QLabel("2 Error, 3 Peringatan")
    summary_title.setStyleSheet("font-size:18px; font-weight:750; color:#B91C1C;")
    summary_text.addWidget(summary_title)
    summary_text.addWidget(muted_label("Ditemukan 5 masalah dalam project ini"))
    summary_layout.addWidget(error_icon)
    summary_layout.addLayout(summary_text, 1)
    summary_layout.addWidget(make_primary_button("Validasi Ulang"))
    layout.addWidget(summary)

    tabs = QTabWidget()
    tab_names = [
        "Semua (5)",
        "Project (1)",
        "Media (1)",
        "Scene (1)",
        "AI (1)",
        "Render (1)",
    ]
    issues = [
        (
            "ERROR",
            "A037 MISSING — Scene 12, 13",
            "File media tidak ditemukan. Digunakan di Scene 12 dan Scene 13.",
            "Relink",
        ),
        (
            "ERROR",
            "Subtitle cue tumpang tindih",
            "Terdapat 3 subtitle yang saling tumpang tindih pada Scene 05.",
            "Buka Subtitle",
        ),
        (
            "PERINGATAN",
            "Durasi scene terlalu pendek",
            "Scene 04 hanya 0,8 detik; disarankan minimal 2 detik.",
            "Buka Scene",
        ),
        (
            "PERINGATAN",
            "Audio tidak normalisasi",
            "Audio pada track A1 (voiceover.mp3) belum dinormalisasi.",
            "Perbaiki Audio",
        ),
        (
            "PERINGATAN",
            "Provider Gemini quota",
            "Sisa quota hanya 12%. Proses AI mungkin gagal jika quota habis.",
            "Buka Provider",
        ),
    ]

    for name in tab_names:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(4, 14, 4, 6)
        page_layout.setSpacing(10)
        if name.startswith("Semua"):
            error_heading = QLabel("Error (2)")
            error_heading.setStyleSheet("font-size:15px; font-weight:750;")
            page_layout.addWidget(error_heading)
            for index, (severity, issue_title, description, action) in enumerate(issues):
                if index == 2:
                    warning_heading = QLabel("Peringatan (3)")
                    warning_heading.setStyleSheet("font-size:15px; font-weight:750; margin-top:8px;")
                    page_layout.addWidget(warning_heading)
                row_frame = QFrame()
                is_error = severity == "ERROR"
                accent = "#DC2626" if is_error else "#F59E0B"
                row_frame.setStyleSheet(
                    "QFrame {background:#FFFFFF; border:1px solid #E2E8F0; "
                    f"border-left:4px solid {accent}; border-radius:6px;}}"
                )
                row = QHBoxLayout(row_frame)
                row.setContentsMargins(12, 11, 10, 11)
                badge = QLabel("!" if is_error else "▲")
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setFixedSize(30, 30)
                badge.setStyleSheet(
                    f"color:{accent}; background:#FFF7ED; border:none; font-weight:800;"
                )
                block = QVBoxLayout()
                title_label = QLabel(issue_title)
                title_label.setStyleSheet("font-weight:700; border:none;")
                description_label = muted_label(description)
                description_label.setStyleSheet("color:#64748B; border:none;")
                block.addWidget(title_label)
                block.addWidget(description_label)
                action_button = QPushButton(action)
                action_button.setStyleSheet(
                    "color:#1D4ED8; border:none; font-weight:650; background:transparent;"
                )
                row.addWidget(badge)
                row.addLayout(block, 1)
                row.addWidget(action_button)
                page_layout.addWidget(row_frame)
        page_layout.addStretch(1)
        tabs.addTab(page, name)

    layout.addWidget(tabs, 1)
    return dialog
