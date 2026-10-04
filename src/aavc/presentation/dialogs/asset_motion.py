from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from aavc.domain.project.models import AnimationAssignment, Scene

NATIVE_MOTION_CHOICES = ("Rise", "Pan", "Drift")


@dataclass(frozen=True, slots=True)
class AssetMotionDialogResult:
    action: Literal["apply", "remove"]
    asset_id: str
    assignment: AnimationAssignment | None = None


def find_asset_motion_assignment(
    assignments: tuple[AnimationAssignment, ...],
    scene_number: int,
    asset_id: str,
) -> AnimationAssignment | None:
    return next(
        (
            item
            for item in assignments
            if item.scene_number == scene_number and item.asset_id == asset_id
        ),
        None,
    )


def show_asset_motion_dialog(
    parent: Any,
    scene: Scene,
    assignments: tuple[AnimationAssignment, ...],
) -> AssetMotionDialogResult | None:
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
    )

    dialog = QDialog(parent)
    dialog.setWindowTitle(f"Animasi Aset — Scene {scene.scene_number:02d}")
    dialog.setModal(True)
    dialog.resize(430, 320)

    root = QVBoxLayout(dialog)
    intro = QLabel(
        "Fase 1 hanya mengekspos motion yang sudah benar-benar dikompilasi ke FFmpeg: "
        "Rise, Pan, dan Drift. Preview editor tetap statis."
    )
    intro.setWordWrap(True)
    root.addWidget(intro)

    form = QFormLayout()
    asset_combo = QComboBox()
    asset_combo.addItems(list(scene.asset_ids))
    enter_combo = QComboBox()
    enter_combo.addItems(list(NATIVE_MOTION_CHOICES))
    exit_combo = QComboBox()
    exit_combo.addItems(list(NATIVE_MOTION_CHOICES))
    intensity = QDoubleSpinBox()
    intensity.setRange(0.0, 2.0)
    intensity.setDecimals(2)
    intensity.setSingleStep(0.1)
    intensity.setValue(1.0)
    form.addRow("Aset", asset_combo)
    form.addRow("Efek masuk", enter_combo)
    form.addRow("Efek keluar", exit_combo)
    form.addRow("Intensitas", intensity)
    root.addLayout(form)

    status = QLabel()
    status.setWordWrap(True)
    status.setStyleSheet("color:#64748B; font-size:9px;")
    root.addWidget(status)

    buttons = QHBoxLayout()
    remove_button = QPushButton("Hapus Animasi Aset")
    cancel_button = QPushButton("Batal")
    apply_button = QPushButton("Terapkan Animasi Aset")
    apply_button.setDefault(True)
    buttons.addWidget(remove_button)
    buttons.addStretch(1)
    buttons.addWidget(cancel_button)
    buttons.addWidget(apply_button)
    root.addLayout(buttons)

    result: list[AssetMotionDialogResult] = []

    def current_assignment() -> AnimationAssignment | None:
        return find_asset_motion_assignment(
            assignments,
            scene.scene_number,
            asset_combo.currentText(),
        )

    def refresh_form() -> None:
        assignment = current_assignment()
        if assignment is None:
            enter_combo.setCurrentText("Rise")
            exit_combo.setCurrentText("Drift")
            intensity.setValue(1.0)
            remove_button.setEnabled(False)
            status.setText("Belum ada assignment animasi pada aset ini.")
            return

        remove_button.setEnabled(True)
        intensity.setValue(max(0.0, min(2.0, assignment.intensity)))
        native_enter = assignment.enter_effect in NATIVE_MOTION_CHOICES
        native_exit = assignment.exit_effect in NATIVE_MOTION_CHOICES
        enter_combo.setCurrentText(assignment.enter_effect if native_enter else "Rise")
        exit_combo.setCurrentText(assignment.exit_effect if native_exit else "Drift")
        if native_enter and native_exit:
            status.setText(
                f"Assignment aktif: {assignment.enter_effect} → {assignment.exit_effect}."
            )
        else:
            status.setText(
                "Assignment lama memakai efek yang belum native phase 1. "
                "Terapkan akan menggantinya dengan pilihan Rise/Pan/Drift; "
                "Hapus akan menghapus assignment tersebut."
            )

    def apply_selection() -> None:
        existing = current_assignment()
        assignment = AnimationAssignment(
            scene_number=scene.scene_number,
            asset_id=asset_combo.currentText(),
            enter_effect=enter_combo.currentText(),
            exit_effect=exit_combo.currentText(),
            intensity=float(intensity.value()),
            locked=existing.locked if existing is not None else False,
        )
        result.append(
            AssetMotionDialogResult(
                action="apply",
                asset_id=assignment.asset_id,
                assignment=assignment,
            )
        )
        dialog.accept()

    def remove_selection() -> None:
        if current_assignment() is None:
            return
        result.append(
            AssetMotionDialogResult(
                action="remove",
                asset_id=asset_combo.currentText(),
            )
        )
        dialog.accept()

    asset_combo.currentIndexChanged.connect(lambda _index: refresh_form())
    apply_button.clicked.connect(apply_selection)
    remove_button.clicked.connect(remove_selection)
    cancel_button.clicked.connect(dialog.reject)
    refresh_form()

    if dialog.exec() != QDialog.DialogCode.Accepted or not result:
        return None
    return result[0]
