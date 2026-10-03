from __future__ import annotations

from typing import Any

from aavc.presentation.widgets.common import make_primary_button, muted_label


def create_validation_dialog(parent: Any = None) -> Any:
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    dialog = QDialog(parent)
    dialog.setWindowTitle("Pusat Error / Validasi")
    dialog.resize(980, 720)

    layout = QVBoxLayout(dialog)
    header = QHBoxLayout()
    title = QLabel("2 Error, 3 Peringatan")
    title.setStyleSheet("font-size:20px; font-weight:700; color:#DC2626;")
    header.addWidget(title)
    header.addStretch(1)
    header.addWidget(make_primary_button("Validasi Ulang"))
    layout.addLayout(header)

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
        ("ERROR", "A037 MISSING — Scene 12, 13", "File media tidak ditemukan.", "Relink"),
        (
            "ERROR",
            "Subtitle cue tumpang tindih",
            "Terdapat 3 subtitle yang saling tumpang tindih.",
            "Buka Subtitle",
        ),
        (
            "PERINGATAN",
            "Durasi scene terlalu pendek",
            "Scene 04 hanya 0,8 detik.",
            "Buka Scene",
        ),
        (
            "PERINGATAN",
            "Audio tidak normalisasi",
            "voiceover.mp3 belum dinormalisasi.",
            "Perbaiki Audio",
        ),
        (
            "PERINGATAN",
            "Provider Gemini quota",
            "Sisa quota hanya 12%.",
            "Buka Provider",
        ),
    ]

    for name in tab_names:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        if name.startswith("Semua"):
            for severity, issue_title, description, action in issues:
                row = QHBoxLayout()
                block = QVBoxLayout()
                title_label = QLabel(f"{severity}  ·  {issue_title}")
                color = "#DC2626" if severity == "ERROR" else "#B45309"
                title_label.setStyleSheet(f"font-weight:600; color:{color};")
                block.addWidget(title_label)
                block.addWidget(muted_label(description))
                row.addLayout(block, 1)
                row.addWidget(QPushButton(action))
                page_layout.addLayout(row)
        page_layout.addStretch(1)
        tabs.addTab(page, name)

    layout.addWidget(tabs)
    return dialog
