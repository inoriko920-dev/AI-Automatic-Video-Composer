from __future__ import annotations

from pathlib import Path
from typing import Any

from aavc.domain.project.models import ProjectState
from aavc.presentation.project_view import (
    AssetView,
    SceneView,
    build_asset_views,
    build_project_summary,
    build_scene_views,
)
from aavc.presentation.widgets.common import muted_label, section_title
from aavc.presentation.widgets.editor_shell import create_editor_shell


def _scene_page(scenes: tuple[SceneView, ...]) -> Any:
    from PySide6.QtWidgets import QListWidget, QListWidgetItem

    widget = QListWidget()
    widget.setSpacing(4)
    for scene in scenes:
        assets = ", ".join(scene.asset_ids)
        item = QListWidgetItem(
            f"{scene.scene_number:02d}. Scene {scene.scene_number:02d}     {scene.mode}\n"
            f"Aset: {assets}\nDurasi: {scene.duration_label}"
        )
        widget.addItem(item)
    if scenes:
        widget.setCurrentRow(0)
    return widget


def _asset_page(assets: tuple[AssetView, ...]) -> Any:
    from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(8, 8, 8, 8)
    ready = sum(asset.status == "READY" for asset in assets)
    layout.addWidget(QLabel(f"Aset project: {len(assets)} · READY {ready} · Belum READY {len(assets) - ready}"))

    listing = QListWidget()
    listing.setSpacing(3)
    for asset in assets:
        status_icon = "✓" if asset.status == "READY" else "⚠"
        quote = asset.source_quote.replace("\\N", " ")
        item = QListWidgetItem(
            f"{status_icon} {asset.asset_id} · {asset.status}\n"
            f"{asset.file_label}\n{quote}"
        )
        listing.addItem(item)
    layout.addWidget(listing, 1)
    return page


def _overview_page(project: ProjectState) -> Any:
    from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

    summary = build_project_summary(project)
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(12)
    layout.addWidget(section_title("Project Overview"))

    card = QFrame()
    card.setProperty("panel", True)
    card_layout = QVBoxLayout(card)
    title = QLabel(summary.title)
    title.setStyleSheet("font-size:15px; font-weight:700;")
    card_layout.addWidget(title)
    for text in [
        f"Resolusi        {summary.resolution}",
        f"Frame Rate      {summary.fps} fps",
        f"Durasi          {summary.duration_label} ({summary.scene_count} scene)",
        f"Aset             {summary.ready_count}/{summary.asset_count} READY",
        f"Narasi           {summary.narration_label}",
        f"Subtitle         {summary.subtitle_label}",
    ]:
        card_layout.addWidget(muted_label(text))
    layout.addWidget(card)

    if summary.not_ready_count:
        warning = QLabel(f"⚠ {summary.not_ready_count} aset belum READY")
        warning.setStyleSheet(
            "color:#B45309; background:#FFFBEB; border:1px solid #FDE68A; "
            "border-radius:6px; padding:8px; font-weight:650;"
        )
        layout.addWidget(warning)
    else:
        ready = QLabel("✓ Semua aset READY")
        ready.setStyleSheet(
            "color:#15803D; background:#F0FDF4; border:1px solid #BBF7D0; "
            "border-radius:6px; padding:8px; font-weight:650;"
        )
        layout.addWidget(ready)

    layout.addStretch(1)
    return page


def create_live_editor_overview(project: ProjectState) -> Any:
    parts = create_editor_shell("overview")
    scenes = build_scene_views(project)
    assets = build_asset_views(project)
    summary = build_project_summary(project)

    parts.left_tabs.clear()
    parts.left_tabs.addTab(_scene_page(scenes), "Scene")
    parts.left_tabs.addTab(_asset_page(assets), "Aset")
    parts.left_tabs.setCurrentIndex(0)

    parts.right_tabs.removeTab(0)
    parts.right_tabs.insertTab(0, _overview_page(project), "Layout")
    parts.right_tabs.setCurrentIndex(0)

    parts.preview_label.clear()
    parts.preview_label.setText(
        "Pratinjau project nyata belum terhubung pada tahap ini.\n"
        "Scene dan aset di panel kiri berasal dari ProjectState aktif."
    )
    parts.preview_label.setStyleSheet(
        "border:1px solid #CBD5E1; background:#F8FAFD; color:#64748B; padding:24px;"
    )
    parts.timeline.setEnabled(False)
    parts.timeline.setToolTip(
        "Timeline masih berupa shell visual pada tahap ini dan belum membaca ProjectState."
    )

    status = "✓ Project siap" if summary.not_ready_count == 0 else f"⚠ {summary.not_ready_count} aset belum READY"
    source_name = Path(project.source_docx).name
    parts.status_label.setText(
        f"{status}   ·   {project.title}   ·   {summary.scene_count} scene   ·   "
        f"{summary.resolution}   ·   {summary.fps} fps   ·   {summary.duration_label}   ·   "
        f"Source: {source_name}"
    )
    return parts.root
