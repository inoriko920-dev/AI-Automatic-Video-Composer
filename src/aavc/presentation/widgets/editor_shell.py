from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aavc.presentation.design_tokens import COLORS, METRICS
from aavc.presentation.widgets.common import make_primary_button, muted_label, section_title


@dataclass(slots=True)
class EditorShellParts:
    root: Any
    left_tabs: Any
    preview_frame: Any
    preview_label: Any
    right_tabs: Any
    timeline: Any
    status_label: Any


def _asset_grid() -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

    container = QWidget()
    grid = QGridLayout(container)
    grid.setContentsMargins(8, 8, 8, 8)
    grid.setSpacing(8)
    samples = [
        ("A001", "Scene 1", "READY"),
        ("A002", "Scene 1", "READY"),
        ("A003", "Scene 2", "READY"),
        ("A004", "Scene 2", "READY"),
        ("A005", "Scene 3", "READY"),
        ("A006", "Scene 3", "READY"),
        ("A007", "Scene 4", "READY"),
        ("A008", "Scene 4", "READY"),
        ("A009", "Scene 5", "READY"),
        ("A010", "Scene 5", "READY"),
        ("A011", "Scene 6", "MISSING"),
        ("A012", "Scene 6", "READY"),
    ]
    for index, (asset_id, scene, status) in enumerate(samples):
        card = QFrame()
        card.setProperty("panel", True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        thumb = QLabel("▧")
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setMinimumHeight(54)
        thumb.setStyleSheet(
            f"background:{COLORS.panel}; color:{COLORS.muted}; font-size:22px;"
        )
        badge = QLabel(status)
        badge.setProperty("badge", "ready" if status == "READY" else "warning")
        layout.addWidget(thumb)
        layout.addWidget(QLabel(f"{asset_id}   {scene}"))
        layout.addWidget(badge)
        grid.addWidget(card, index // 2, index % 2)
    return container


def _scene_list() -> Any:
    from PySide6.QtWidgets import QListWidget, QListWidgetItem

    widget = QListWidget()
    for number in range(1, 13):
        mode = "DOUBLE" if number % 3 == 1 else "SINGLE"
        ids = (
            f"A{number * 2 - 1:03d}, A{number * 2:03d}"
            if mode == "DOUBLE"
            else f"A{number:03d}"
        )
        widget.addItem(QListWidgetItem(f"Scene {number:02d}   {mode}\n{ids}    READY"))
    widget.setCurrentRow(3)
    return widget


def _preview_widget(mode: str) -> tuple[Any, Any, Any]:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget,
    )

    outer = QWidget()
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(8, 8, 8, 6)
    header = QHBoxLayout()
    header.addWidget(QLabel("Pratinjau: 1920 × 1080 (16:9)"))
    header.addStretch(1)
    header.addWidget(QLabel("Sesuaikan   100%"))
    layout.addLayout(header)

    frame = QFrame()
    frame.setStyleSheet(
        f"background:{COLORS.monitor_matte}; border:1px solid #111827;"
    )
    frame_layout = QVBoxLayout(frame)
    frame_layout.setContentsMargins(28, 28, 28, 28)
    canvas = QLabel()
    canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
    canvas.setMinimumSize(640, 360)
    if mode == "single":
        text = "SCENE 08 — SINGLE\n\n[ A014 ]\n\nSatu aset independen di area preview"
    elif mode == "double":
        text = (
            "SCENE 08 — DOUBLE\n\n[ A014 ]      [ A015 ]\n\n"
            "Dua aset independen, bukan bitmap gabungan"
        )
    elif mode == "subtitle":
        text = (
            "PREVIEW DOKUMENTER\n\nVisual scene + background\n\n────────────────────────\n"
            "Pagi yang cerah di desa Bromo,\nseekor kucing kecil berjalan di taman."
        )
    else:
        text = "PREVIEW PROJECT\n\nScene 08 / A014\n\n16:9"
    canvas.setText(text)
    canvas.setStyleSheet("color:#F8FAFC; font-size:20px; font-weight:600;")
    frame_layout.addStretch(1)
    frame_layout.addWidget(canvas)
    frame_layout.addStretch(1)
    layout.addWidget(frame, 1)

    transport = QHBoxLayout()
    transport.addWidget(QLabel("00:00:12:08 / 00:01:28:00"))
    transport.addStretch(1)
    for label in ["◀", "▶", "■"]:
        transport.addWidget(QPushButton(label))
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(34)
    transport.addWidget(slider, 1)
    layout.addLayout(transport)
    return outer, frame, canvas


def _layout_inspector(mode: str) -> Any:
    from PySide6.QtWidgets import (
        QComboBox,
        QFormLayout,
        QHBoxLayout,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.addWidget(section_title("Layout & Transform"))
    target = "Target: A014 / A015" if mode == "double" else "Target: A014"
    layout.addWidget(muted_label(target))
    form = QFormLayout()
    for label, value in [("Posisi X", 0), ("Posisi Y", -18), ("Skala", 84)]:
        spin = QSpinBox()
        spin.setRange(-500, 500)
        spin.setValue(value)
        form.addRow(label, spin)
    fit = QComboBox()
    fit.addItems(["Fit", "Fill", "Original"])
    form.addRow("Mode Fit", fit)
    if mode == "double":
        spacing = QSpinBox()
        spacing.setRange(0, 200)
        spacing.setValue(28)
        form.addRow("Jarak Pasangan", spacing)
    layout.addLayout(form)
    row = QHBoxLayout()
    row.addWidget(QPushButton("Reset"))
    row.addWidget(make_primary_button("Terapkan"))
    layout.addLayout(row)
    layout.addStretch(1)
    return widget


def _subtitle_inspector() -> Any:
    from PySide6.QtWidgets import (
        QCheckBox,
        QFormLayout,
        QHBoxLayout,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    tabs = QTabWidget()
    text_page = QWidget()
    layout = QVBoxLayout(text_page)
    layout.addWidget(section_title("Daftar Subtitle (8 cue)"))
    cue_list = QListWidget()
    cues = [
        "00:00:00:00 → 00:00:04:12\nPagi yang cerah di desa Bromo...",
        "00:00:04:12 → 00:00:08:20\nIa melihat bunga berwarna-warni...",
        "00:00:08:10 → 00:00:12:00  ⚠\nLalu melompat ke arah pagar kayu...",
        "00:00:12:00 → 00:00:16:15\nUdara segar membuatnya bersemangat.",
    ]
    for cue in cues:
        cue_list.addItem(QListWidgetItem(cue))
    cue_list.setCurrentRow(2)
    layout.addWidget(cue_list, 1)
    layout.addWidget(section_title("Edit Cue"))
    text = QTextEdit("Lalu melompat ke arah pagar kayu dengan lincah.")
    text.setMaximumHeight(70)
    layout.addWidget(text)
    form = QFormLayout()
    form.addRow("Waktu Mulai", QLineEdit("00:00:08:10"))
    form.addRow("Waktu Selesai", QLineEdit("00:00:12:00"))
    layout.addLayout(form)
    row = QHBoxLayout()
    row.addWidget(QPushButton("Pisah Cue"))
    row.addWidget(QPushButton("Gabung"))
    row.addWidget(QPushButton("Muat Ulang SRT"))
    layout.addLayout(row)
    layout.addWidget(QCheckBox("Kunci timing"))
    tabs.addTab(text_page, "Teks")
    tabs.addTab(QWidget(), "Gaya")
    tabs.addTab(QWidget(), "Animasi")
    return tabs


def _ai_placeholder() -> Any:
    from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(section_title("AI Agent"))
    layout.addWidget(muted_label("Scope: Seluruh Proyek · Scene 08 · A014"))
    for text in [
        "Acak animasi scene 1–10",
        "Cari aset missing",
        "Atur scene ini lebih rapat",
    ]:
        layout.addWidget(QPushButton(text))
    layout.addStretch(1)
    layout.addWidget(QLineEdit("Tulis perintah..."))
    layout.addWidget(make_primary_button("Kirim"))
    return widget


def _timeline_widget() -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

    outer = QFrame()
    outer.setProperty("panel", True)
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(6, 6, 6, 6)
    layout.addWidget(
        QLabel("Timeline     00:00:00     00:00:20     00:00:40     00:01:00     00:01:20")
    )
    grid = QGridLayout()
    grid.setHorizontalSpacing(3)
    grid.setVerticalSpacing(4)
    tracks = [
        ("V2  Elemen", ["A008", "", "A014", ""]),
        ("V1  Video", ["Sc01  Sc02", "Sc03  Sc04", "Sc05  Sc06", "Sc07"]),
        ("A1  Audio", ["background-music.mp3", "", "", ""]),
        ("A2  Narasi", ["narasi-001.mp3", "", "", ""]),
        (
            "S1  Subtitle",
            ["Pagi yang cerah...", "Seekor kucing...", "Ia melihat bunga...", "Lalu melompat..."],
        ),
    ]
    for row_index, (name, blocks) in enumerate(tracks):
        name_label = QLabel(name)
        name_label.setMinimumWidth(92)
        grid.addWidget(name_label, row_index, 0)
        for column_index, block in enumerate(blocks, start=1):
            label = QLabel(block)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if row_index in {0, 1, 4}:
                color = "#DBEAFE"
            elif row_index == 2:
                color = "#DCFCE7"
            else:
                color = "#F3E8FF"
            label.setStyleSheet(
                f"background:{color}; border:1px solid #CBD5E1; "
                "border-radius:4px; padding:8px;"
            )
            grid.addWidget(label, row_index, column_index)
    layout.addLayout(grid, 1)
    return outer


def create_editor_shell(mode: str = "overview") -> EditorShellParts:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLineEdit, QSplitter, QTabWidget, QVBoxLayout, QWidget

    root = QWidget()
    vertical = QVBoxLayout(root)
    vertical.setContentsMargins(0, 0, 0, 0)
    vertical.setSpacing(0)
    upper = QSplitter(Qt.Orientation.Horizontal)

    left = QTabWidget()
    left.setMinimumWidth(METRICS.left_min_w)
    left.setMaximumWidth(520)
    assets_page = QWidget()
    assets_layout = QVBoxLayout(assets_page)
    assets_layout.setContentsMargins(8, 8, 8, 8)
    assets_layout.addWidget(QLineEdit("Cari Asset ID..."))
    assets_layout.addWidget(_asset_grid(), 1)
    left.addTab(assets_page, "Aset")
    left.addTab(_scene_list(), "Scene")

    preview_mode = mode if mode in {"single", "double", "subtitle"} else "overview"
    preview, frame, preview_label = _preview_widget(preview_mode)

    right = QTabWidget()
    right.setMinimumWidth(300)
    right.setMaximumWidth(METRICS.right_max_w)
    if mode == "subtitle":
        right.addTab(_subtitle_inspector(), "Subtitle")
        right.addTab(_ai_placeholder(), "AI Agent")
    else:
        right.addTab(_layout_inspector(mode), "Layout")
        right.addTab(QWidget(), "Animasi")
        right.addTab(_ai_placeholder(), "AI Agent")

    upper.addWidget(left)
    upper.addWidget(preview)
    upper.addWidget(right)
    upper.setSizes([METRICS.left_ref_w, 1260, METRICS.right_ref_w])

    timeline = _timeline_widget()
    timeline.setMinimumHeight(METRICS.timeline_min_h)
    outer = QSplitter(Qt.Orientation.Vertical)
    outer.addWidget(upper)
    outer.addWidget(timeline)
    outer.setSizes([660, METRICS.timeline_ref_h])
    vertical.addWidget(outer, 1)

    status = muted_label(
        "Proyek disimpan otomatis   ·   Scene 08   ·   1920 × 1080   ·   30 fps   ·   "
        "Durasi 00:01:28:00"
    )
    status.setMinimumHeight(METRICS.status_h)
    vertical.addWidget(status)
    return EditorShellParts(root, left, frame, preview_label, right, timeline, status)
