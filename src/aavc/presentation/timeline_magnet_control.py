from __future__ import annotations

from typing import Any

TIMELINE_MAGNET_ENABLED_PROPERTY = "aavcTimelineMagnetEnabled"
TIMELINE_MAGNET_BUTTON_OBJECT_NAME = "TimelineMagnetToggle"


def normalize_timeline_magnet_enabled(value: object | None) -> bool:
    """Normalize a session property value; unset means Magnet is enabled by default."""

    if value is None:
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"0", "false", "off", "no"}:
            return False
        if normalized in {"1", "true", "on", "yes"}:
            return True
    return bool(value)


def timeline_magnet_active(enabled: bool, *, alt_bypass: bool = False) -> bool:
    """Return whether magnetic snapping should apply for the current gesture."""

    return bool(enabled) and not bool(alt_bypass)


def timeline_magnet_enabled(owner: Any) -> bool:
    """Read the session-only Magnet state from the owning window."""

    return normalize_timeline_magnet_enabled(
        owner.property(TIMELINE_MAGNET_ENABLED_PROPERTY)
    )


def timeline_magnet_active_for_owner(
    owner: Any,
    *,
    alt_bypass: bool = False,
) -> bool:
    return timeline_magnet_active(
        timeline_magnet_enabled(owner),
        alt_bypass=alt_bypass,
    )


def install_timeline_magnet_control(root: Any) -> bool:
    """Install a compact session-only Magnet toggle beside the timeline zoom control."""

    from PySide6.QtWidgets import QSpinBox, QToolButton

    zoom_box = root.findChild(QSpinBox, "TimelineZoomPercent")
    if zoom_box is None:
        return False
    timeline = zoom_box.parentWidget()
    if timeline is None or timeline.layout() is None:
        return False

    owner: Any = timeline.window()
    enabled = timeline_magnet_enabled(owner)
    owner.setProperty(TIMELINE_MAGNET_ENABLED_PROPERTY, enabled)

    header_layout = timeline.layout().itemAt(0).layout() if timeline.layout().count() else None
    if header_layout is None:
        return False

    existing = root.findChild(QToolButton, TIMELINE_MAGNET_BUTTON_OBJECT_NAME)
    if existing is not None:
        existing.setChecked(enabled)
        return True

    button = QToolButton(timeline)
    button.setObjectName(TIMELINE_MAGNET_BUTTON_OBJECT_NAME)
    button.setCheckable(True)
    button.setChecked(enabled)
    button.setToolTip(
        "Magnetic snapping timeline. Matikan untuk edit bebas; tahan Alt untuk bypass sementara."
    )

    def refresh_button(checked: bool) -> None:
        owner.setProperty(TIMELINE_MAGNET_ENABLED_PROPERTY, bool(checked))
        button.setText("Magnet ON" if checked else "Magnet OFF")
        button.setStyleSheet(
            "QToolButton { padding: 2px 7px; font-size: 9px; }"
            "QToolButton:checked { color: #1D4ED8; font-weight: 600; }"
        )
        if not checked:
            from aavc.presentation.timeline_snap_guide import hide_timeline_snap_guide

            hide_timeline_snap_guide(root)
        status_bar = owner.statusBar() if hasattr(owner, "statusBar") else None
        if status_bar is not None:
            state = "aktif" if checked else "nonaktif"
            status_bar.showMessage(
                f"Magnet timeline {state}. Tahan Alt untuk bypass sementara saat Magnet aktif.",
                4500,
            )

    button.toggled.connect(refresh_button)
    refresh_button(enabled)
    header_layout.insertWidget(max(0, header_layout.count() - 2), button)
    root._aavc_timeline_magnet_button = button
    return True
