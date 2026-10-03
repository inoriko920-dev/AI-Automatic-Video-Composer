from __future__ import annotations

from aavc.presentation.widgets.common import make_primary_button, muted_label


def create_new_project_screen(on_back, on_continue):
    from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

    root=QWidget(); outer=QVBoxLayout(root); outer.setContentsMargins(120,60,120,60)
    title=QLabel("Proyek Baru"); title.setStyleSheet("font-size:26px; font-weight:700;"); outer.addWidget(title)
    outer.addWidget(muted_label("Langkah 1 dari 4  ·  Pilih Scene DOCX"))
    card=QFrame(); card.setProperty("panel", True); card.setMaximumWidth(980); inner=QVBoxLayout(card); inner.setContentsMargins(28,28,28,28); inner.setSpacing(16)
    inner.addWidget(QLabel("Scene DOCX dari Prompt 1")); path=QLineEdit(); path.setPlaceholderText("Pilih scene_asset_[Judul].docx")
    browse=QPushButton("Pilih DOCX…")
    def browse_file():
        chosen,_=QFileDialog.getOpenFileName(root,"Pilih Scene DOCX","","DOCX (*.docx)")
        if chosen: path.setText(chosen)
    browse.clicked.connect(browse_file)
    row=QHBoxLayout(); row.addWidget(path,1); row.addWidget(browse); inner.addLayout(row)
    inner.addWidget(muted_label("File akan diparse dan divalidasi. Scene harus memiliki visual_count 1 atau 2 dan Asset ID canonical Axxx."))
    footer=QHBoxLayout(); back=QPushButton("Kembali"); next_btn=make_primary_button("Lanjut"); back.clicked.connect(on_back); next_btn.clicked.connect(on_continue); footer.addWidget(back); footer.addStretch(1); footer.addWidget(next_btn); inner.addLayout(footer)
    outer.addWidget(card); outer.addStretch(1); return root
