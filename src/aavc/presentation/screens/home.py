from __future__ import annotations

from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title


def create_home_screen(on_new_project, on_open_editor):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

    root = QWidget(); layout = QVBoxLayout(root); layout.setContentsMargins(72, 52, 72, 52); layout.setSpacing(18)
    title = QLabel("AI Automatic Video Composer"); title.setStyleSheet("font-size:28px; font-weight:700;")
    layout.addWidget(title); layout.addWidget(muted_label("Susun scene, aset, animasi, subtitle, dan render dalam satu workflow."))
    actions = QHBoxLayout(); new_btn = make_primary_button("Proyek Baru"); open_btn = QPushButton("Buka Proyek")
    new_btn.clicked.connect(on_new_project); open_btn.clicked.connect(on_open_editor); actions.addWidget(new_btn); actions.addWidget(open_btn); actions.addStretch(1); layout.addLayout(actions)
    layout.addSpacing(16); layout.addWidget(section_title("Project Terbaru"))
    cards = QHBoxLayout()
    for name, meta in [("Liburan ke Bromo", "Terakhir dibuka hari ini · 47 scene"), ("Dokumenter AI", "Kemarin · 32 scene"), ("Album Video", "2 hari lalu · 18 scene")]:
        card=QFrame(); card.setProperty("panel", True); card.setMinimumHeight(150); c=QVBoxLayout(card); c.addWidget(QLabel("▣")); n=QLabel(name); n.setStyleSheet("font-size:16px; font-weight:600;"); c.addWidget(n); c.addWidget(muted_label(meta)); b=QPushButton("Buka"); b.clicked.connect(on_open_editor); c.addWidget(b); cards.addWidget(card)
    layout.addLayout(cards); layout.addStretch(1)
    return root
