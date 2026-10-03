from __future__ import annotations

from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title


def create_home_screen(on_new_project, on_open_editor):
    from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setContentsMargins(72, 52, 72, 52)
    layout.setSpacing(18)

    title = QLabel("AI Automatic Video Composer")
    title.setStyleSheet("font-size:28px; font-weight:700;")
    layout.addWidget(title)
    layout.addWidget(
        muted_label(
            "Susun scene, aset, animasi, subtitle, dan render dalam satu workflow."
        )
    )

    actions = QHBoxLayout()
    new_button = make_primary_button("Proyek Baru")
    open_button = QPushButton("Buka Proyek")
    new_button.clicked.connect(on_new_project)
    open_button.clicked.connect(on_open_editor)
    actions.addWidget(new_button)
    actions.addWidget(open_button)
    actions.addStretch(1)
    layout.addLayout(actions)

    layout.addSpacing(16)
    layout.addWidget(section_title("Project Terbaru"))
    cards = QHBoxLayout()
    samples = [
        ("Liburan ke Bromo", "Terakhir dibuka hari ini · 47 scene"),
        ("Dokumenter AI", "Kemarin · 32 scene"),
        ("Album Video", "2 hari lalu · 18 scene"),
    ]
    for name, metadata in samples:
        card = QFrame()
        card.setProperty("panel", True)
        card.setMinimumHeight(150)
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("▣"))
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size:16px; font-weight:600;")
        card_layout.addWidget(name_label)
        card_layout.addWidget(muted_label(metadata))
        open_card = QPushButton("Buka")
        open_card.clicked.connect(on_open_editor)
        card_layout.addWidget(open_card)
        cards.addWidget(card)
    layout.addLayout(cards)
    layout.addStretch(1)
    return root
