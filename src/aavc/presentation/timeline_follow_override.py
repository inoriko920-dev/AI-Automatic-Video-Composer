from __future__ import annotations

DEFAULT_TIMELINE_FOLLOW_MANUAL_OVERRIDE = False
TIMELINE_FOLLOW_MANUAL_OVERRIDE_PROPERTY = "aavcTimelineFollowManualOverride"


def normalize_timeline_follow_manual_override(value: object) -> bool:
    """Normalize the session-only manual-scroll override flag."""

    if value is None:
        return DEFAULT_TIMELINE_FOLLOW_MANUAL_OVERRIDE
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
    return DEFAULT_TIMELINE_FOLLOW_MANUAL_OVERRIDE


def timeline_follow_may_scroll(
    *,
    requested_follow: bool,
    follow_enabled: bool,
    manual_override: object,
) -> bool:
    """Return whether Follow Playhead may move the viewport for this update."""

    return (
        bool(requested_follow)
        and bool(follow_enabled)
        and not normalize_timeline_follow_manual_override(manual_override)
    )


def timeline_follow_button_text(
    *,
    follow_enabled: bool,
    manual_override: object,
) -> str:
    """Return the compact header label for the effective Follow state."""

    if not follow_enabled:
        return "Follow OFF"
    if normalize_timeline_follow_manual_override(manual_override):
        return "Follow PAUSE"
    return "Follow ON"
