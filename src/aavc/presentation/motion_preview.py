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


def preview_narration_seconds(
    scene_durations: tuple[float, ...],
    scene_index: int,
    local_seconds: float,
) -> float:
    """Map a Scene-local preview time to the global narration timeline."""

    index = int(scene_index)
    if index < 0 or index >= len(scene_durations):
        return 0.0
    normalized = tuple(max(0.0, float(duration)) for duration in scene_durations)
    scene_duration = normalized[index]
    local = max(0.0, min(float(local_seconds), scene_duration))
    return sum(normalized[:index]) + local


def preview_timecode(seconds: float, fps: int) -> str:
    """Format a non-negative preview position as HH:MM:SS:FF."""

    rate = max(1, int(fps))
    position = max(0.0, float(seconds))
    total_frames = max(0, int(round(position * rate)))
    total_seconds, frames = divmod(total_frames, rate)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


def preview_neighbor_scene_index(
    current_index: int,
    scene_count: int,
    step: int,
) -> int | None:
    """Return an adjacent preview Scene index, or None when navigation hits a boundary."""

    count = max(0, int(scene_count))
    current = int(current_index)
    if count == 0 or current < 0 or current >= count or step == 0:
        return None
    target = current + (1 if step > 0 else -1)
    if target < 0 or target >= count:
        return None
    return target


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
