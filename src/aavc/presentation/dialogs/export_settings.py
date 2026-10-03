from __future__ import annotations

from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title


def create_export_dialog(parent=None):
    from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout
    from PySide6.QtCore import Qt

    dialog=QDialog(parent); dialog.setWindowTitle("Ekspor Video"); dialog.resize(980,690)
    layout=QVBoxLayout(dialog); layout.setContentsMargins(24,24,24,24)
    layout.addWidget(section_title("Ekspor Video")); layout.addWidget(muted_label("Atur kualitas final. Preview boleh lebih ringan; render final menggunakan kualitas penuh."))
    form=QFormLayout(); path=QLineEdit(r"D:\Video Projects\Liburan ke Bromo\Hasil Akhir"); name=QLineEdit("Liburan ke Bromo - Final")
    fmt=QComboBox(); fmt.addItems(["MP4 (H.264)","MP4 (H.265)"]); preset=QComboBox(); preset.addItems(["Kualitas Tinggi (Rekomendasi)","YouTube Clean","Documentary Crisp"])
    res=QComboBox(); res.addItems(["1920 × 1080 (Full HD)","2560 × 1440","3840 × 2160 (4K)"]); fps=QComboBox(); fps.addItems(["30 fps","60 fps"])
    form.addRow("Lokasi Output",path); form.addRow("Nama File",name); form.addRow("Format",fmt); form.addRow("Preset",preset); form.addRow("Resolusi",res); form.addRow("Frame Rate",fps)
    layout.addLayout(form); layout.addWidget(QLabel("Bitrate / Kualitas")); q=QSlider(Qt.Orientation.Horizontal); q.setValue(78); layout.addWidget(q)
    sharpen=QComboBox(); sharpen.addItems(["Normal","Tajam Ringan","Documentary Crisp"]); form2=QFormLayout(); form2.addRow("Ketajaman Video",sharpen); subtitle=QComboBox(); subtitle.addItems(["Sertakan Subtitle (Burn-in ke Video)","Tanpa Subtitle"]); form2.addRow("Subtitle",subtitle); layout.addLayout(form2)
    layout.addWidget(QCheckBox("Gunakan akselerasi GPU jika tersedia")); layout.addStretch(1)
    footer=QHBoxLayout(); footer.addWidget(QPushButton("Pengaturan Lanjutan")); footer.addStretch(1); footer.addWidget(QPushButton("Batal")); footer.addWidget(make_primary_button("Mulai Render")); layout.addLayout(footer)
    return dialog
