from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.domain.project.models import SubtitleStyle
from aavc.presentation.subtitle_view import (
    SubtitleCueView,
    build_subtitle_views,
)
from aavc.presentation.widgets.common import (
    make_primary_button,
    muted_label,
    section_title,
)
from aavc.subtitles import (
    STYLE_PRESETS,
    get_style_preset,
    parse_srt,
)


ALIGNMENT_OPTIONS: tuple[tuple[str, int], ...] = (
    ("Bawah Kiri", 1),
    ("Bawah Tengah", 2),
    ("Bawah Kanan", 3),
    ("Tengah Kiri", 4),
    ("Tengah", 5),
    ("Tengah Kanan", 6),
    ("Atas Kiri", 7),
    ("Atas Tengah", 8),
    ("Atas Kanan", 9),
)


def load_subtitle_views(source: str | Path) -> tuple[SubtitleCueView, ...]:
    return build_subtitle_views(parse_srt(source))


def create_live_subtitle_inspector(
    source: str | Path,
    *,
    style: SubtitleStyle | None = None,
    on_apply_style: Callable[[SubtitleStyle], None] | None = None,
    on_reload: Callable[[], None] | None = None,
) -> Any:
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    source_path = Path(source).resolve()
    views = load_subtitle_views(source_path)
    current_style = style or SubtitleStyle()

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
    style_layout.addWidget(section_title("Gaya Subtitle untuk Render"))
    style_layout.addWidget(
        muted_label(
            "Nilai di tab ini disimpan pada ProjectState dan dipakai saat SRT dikompilasi "
            "menjadi ASS untuk burn-in video. Klik Terapkan Gaya lalu Simpan project."
        )
    )

    style_form = QFormLayout()
    preset = QComboBox()
    preset_names = list(STYLE_PRESETS)
    if current_style.preset_name not in preset_names:
        preset_names.append(current_style.preset_name)
    preset.addItems(preset_names)
    preset.setCurrentText(current_style.preset_name)

    font_family = QLineEdit()
    font_size = QSpinBox()
    font_size.setRange(1, 400)
    fill_color = QLineEdit()
    fill_color.setPlaceholderText("#FFFFFF")
    outline_color = QLineEdit()
    outline_color.setPlaceholderText("#111111")
    outline_width = QDoubleSpinBox()
    outline_width.setRange(0.0, 20.0)
    outline_width.setDecimals(2)
    outline_width.setSingleStep(0.25)
    shadow = QDoubleSpinBox()
    shadow.setRange(0.0, 20.0)
    shadow.setDecimals(2)
    shadow.setSingleStep(0.25)
    background_box = QCheckBox("Gunakan kotak background")
    background_opacity = QSpinBox()
    background_opacity.setRange(0, 100)
    background_opacity.setSuffix(" %")
    alignment = QComboBox()
    for label, value in ALIGNMENT_OPTIONS:
        alignment.addItem(label, value)
    margin_v = QSpinBox()
    margin_v.setRange(0, 5000)
    margin_v.setSuffix(" px")

    style_form.addRow("Preset", preset)
    style_form.addRow("Font", font_family)
    style_form.addRow("Ukuran Font", font_size)
    style_form.addRow("Warna Isi", fill_color)
    style_form.addRow("Warna Outline", outline_color)
    style_form.addRow("Lebar Outline", outline_width)
    style_form.addRow("Shadow", shadow)
    style_form.addRow("Background", background_box)
    style_form.addRow("Opacity Background", background_opacity)
    style_form.addRow("Posisi", alignment)
    style_form.addRow("Margin Vertikal", margin_v)
    style_layout.addLayout(style_form)

    def load_style(target: SubtitleStyle) -> None:
        font_family.setText(target.font_family)
        font_size.setValue(target.font_size)
        fill_color.setText(target.fill_color)
        outline_color.setText(target.outline_color)
        outline_width.setValue(target.outline_width)
        shadow.setValue(target.shadow)
        background_box.setChecked(target.background_box)
        background_opacity.setValue(target.background_opacity)
        index = alignment.findData(target.alignment)
        alignment.setCurrentIndex(index if index >= 0 else 1)
        margin_v.setValue(target.margin_v)

    load_style(current_style)

    def load_preset(name: str) -> None:
        if name in STYLE_PRESETS:
            load_style(get_style_preset(name))

    preset.currentTextChanged.connect(load_preset)

    apply_style = make_primary_button("Terapkan Gaya")
    if on_apply_style is None:
        apply_style.setEnabled(False)
        apply_style.setToolTip("Editor gaya belum terhubung ke sesi project.")
    else:

        def apply_current_style() -> None:
            target = SubtitleStyle(
                preset_name=preset.currentText(),
                font_family=font_family.text().strip(),
                font_size=font_size.value(),
                fill_color=fill_color.text().strip(),
                outline_color=outline_color.text().strip(),
                outline_width=float(outline_width.value()),
                shadow=float(shadow.value()),
                background_box=background_box.isChecked(),
                background_opacity=background_opacity.value(),
                alignment=int(alignment.currentData()),
                margin_v=margin_v.value(),
            )
            on_apply_style(target)

        apply_style.clicked.connect(apply_current_style)
    style_layout.addWidget(apply_style)
    style_layout.addWidget(
        muted_label(
            "Preview burn-in subtitle belum tersedia pada layar ini. Hasil final mengikuti "
            "compiler ASS saat Ekspor Video dengan Sertakan Subtitle aktif."
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
