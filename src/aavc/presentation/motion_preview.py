from __future__ import annotations

from dataclasses import dataclass

from aavc.animation import evaluate_effect
from aavc.animation.compiler import is_native_visual_motion_effect
from aavc.domain.project.models import AnimationAssignment


@dataclass(frozen=True, slots=True)
class PreviewMotionOffset:
    x: float = 0.0
    y: float = 0.0


def preview_scrub_seconds(
    value: int,
    maximum: int,
    duration_seconds: float,
) -> float:
    """Map a preview slider position to a clamped scene-local time."""

    duration = max(0.0, float(duration_seconds))
    if duration == 0.0:
        return 0.0
    upper = max(1, int(maximum))
    clamped = max(0, min(int(value), upper))
    return duration * (clamped / upper)


def native_motion_preview_offset(
    assignment: AnimationAssignment | None,
    *,
    time_seconds: float,
    duration_seconds: float,
) -> PreviewMotionOffset:
    """Evaluate phase-one native motion using the same 0.25s timing contract as FFmpeg."""

    if assignment is None or assignment.intensity <= 0:
        return PreviewMotionOffset()

    duration = max(0.001, float(duration_seconds))
    current = max(0.0, min(float(time_seconds), duration))
    window = min(0.25, duration / 2.0)
    intensity = max(0.0, min(2.0, float(assignment.intensity)))
    offset_x = 0.0
    offset_y = 0.0

    for effect, entering in (
        (assignment.enter_effect, True),
        (assignment.exit_effect, False),
    ):
        if not is_native_visual_motion_effect(effect):
            continue
        if entering:
            progress = current / window
        else:
            exit_start = max(0.0, duration - window)
            progress = (current - exit_start) / window
        delta = evaluate_effect(effect, progress, entering=entering)
        offset_x += delta.offset_x * intensity
        offset_y += delta.offset_y * intensity

    return PreviewMotionOffset(offset_x, offset_y)
