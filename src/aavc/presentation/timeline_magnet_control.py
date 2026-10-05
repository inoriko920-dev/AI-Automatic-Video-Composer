from __future__ import annotations

from typing import Any

TIMELINE_MAGNET_ENABLED_PROPERTY = "aavcTimelineMagnetEnabled"
TIMELINE_MAGNET_BUTTON_OBJECT_NAME = "TimelineMagnetToggle"

_runtime_magnet_enabled = True
_runtime_magnet_bypass = False


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


def set_timeline_magnet_runtime_enabled(enabled: bool) -> None:
    global _runtime_magnet_enabled
    _runtime_magnet_enabled = bool(enabled)


def set_timeline_magnet_runtime_bypass(bypass: bool) -> None:
    global _runtime_magnet_bypass
    _runtime_magnet_bypass = bool(bypass)


def timeline_magnet_runtime_active(*, alt_bypass: bool | None = None) -> bool:
    """Return process runtime Magnet state, including Alt/transient bypass."""

    bypass = _runtime_magnet_bypass
    if alt_bypass is None:
        try:
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QApplication

            alt_bypass = bool(
                QApplication.keyboardModifiers() & Qt.KeyboardModifier.AltModifier
            )
        except (ImportError, RuntimeError):
            alt_bypass = False
    return timeline_magnet_active(
        _runtime_magnet_enabled,
        alt_bypass=bypass or bool(alt_bypass),
    )


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

    from PySide6.QtGui import QAction, QKeySequence, QShortcut
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
    set_timeline_magnet_runtime_enabled(enabled)

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

    def apply_state(checked: bool, *, announce: bool) -> None:
        owner.setProperty(TIMELINE_MAGNET_ENABLED_PROPERTY, bool(checked))
        set_timeline_magnet_runtime_enabled(bool(checked))
        button.setText("Magnet ON" if checked else "Magnet OFF")
        button.setStyleSheet(
            "QToolButton { padding: 2px 7px; font-size: 9px; }"
            "QToolButton:checked { color: #1D4ED8; font-weight: 600; }"
        )
        if not checked:
            from aavc.presentation.timeline_snap_guide import hide_timeline_snap_guide

            hide_timeline_snap_guide(root)
        if not announce:
            return
        status_bar = owner.statusBar() if hasattr(owner, "statusBar") else None
        if status_bar is not None:
            state = "aktif" if checked else "nonaktif"
            status_bar.showMessage(
                f"Magnet timeline {state}. Tahan Alt untuk bypass sementara saat Magnet aktif.",
                4500,
            )

    button.toggled.connect(lambda checked: apply_state(bool(checked), announce=True))
    apply_state(enabled, announce=False)
    header_layout.insertWidget(max(0, header_layout.count() - 2), button)
    root._aavc_timeline_magnet_button = button

    def split_without_magnet() -> None:
        split_action = next(
            (
                action
                for action in owner.findChildren(QAction)
                if action.text() == "Split Scene di Playhead"
            ),
            None,
        )
        if split_action is None:
            return
        set_timeline_magnet_runtime_bypass(True)
        try:
            split_action.trigger()
        finally:
            set_timeline_magnet_runtime_bypass(False)

    bypass_shortcut = QShortcut(QKeySequence("Ctrl+Alt+B"), root)
    bypass_shortcut.activated.connect(split_without_magnet)
    root._aavc_timeline_split_without_magnet_shortcut = bypass_shortcut
    return True
