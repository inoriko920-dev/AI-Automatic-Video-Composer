from __future__ import annotations

from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title


def create_validation_dialog(parent=None):
    from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTabWidget, QVBoxLayout, QWidget

    dialog=QDialog(parent); dialog.setWindowTitle("Pusat Error / Validasi"); dialog.resize(980,720)
    layout=QVBoxLayout(dialog); header=QHBoxLayout(); title=QLabel("2 Error, 3 Peringatan"); title.setStyleSheet("font-size:20px; font-weight:700; color:#DC2626;"); header.addWidget(title); header.addStretch(1); header.addWidget(make_primary_button("Validasi Ulang")); layout.addLayout(header)
    tabs=QTabWidget();
    for name in ["Semua (5)","Project (1)","Media (1)","Scene (1)","AI (1)","Render (1)"]:
        page=QWidget(); p=QVBoxLayout(page)
        if name.startswith("Semua"):
            issues=[("ERROR","A037 MISSING — Scene 12, 13","File media tidak ditemukan.","Relink"),("ERROR","Subtitle cue tumpang tindih","Terdapat 3 subtitle yang saling tumpang tindih.","Buka Subtitle"),("PERINGATAN","Durasi scene terlalu pendek","Scene 04 hanya 0,8 detik.","Buka Scene"),("PERINGATAN","Audio tidak normalisasi","voiceover.mp3 belum dinormalisasi.","Perbaiki Audio"),("PERINGATAN","Provider Gemini quota","Sisa quota hanya 12%.","Buka Provider")]
            for sev, ttl, desc, action in issues:
                row=QHBoxLayout(); block=QVBoxLayout(); t=QLabel(f"{sev}  ·  {ttl}"); t.setStyleSheet("font-weight:600;" + ("color:#DC2626;" if sev=="ERROR" else "color:#B45309;")); block.addWidget(t); block.addWidget(muted_label(desc)); row.addLayout(block,1); row.addWidget(QPushButton(action)); p.addLayout(row)
        p.addStretch(1); tabs.addTab(page,name)
    layout.addWidget(tabs); return dialog
