from __future__ import annotations

from aavc.domain.project.models import AnimationAssignment

NATIVE_VISUAL_MOTION_EFFECTS = frozenset({"Rise", "Pan", "Drift"})


def is_native_visual_motion_effect(name: str) -> bool:
    return name in NATIVE_VISUAL_MOTION_EFFECTS


def assignment_has_native_motion(
    assignment: AnimationAssignment | None,
) -> bool:
    if assignment is None or assignment.intensity <= 0:
        return False
    return (
        is_native_visual_motion_effect(assignment.enter_effect)
        or is_native_visual_motion_effect(assignment.exit_effect)
    )


def _motion_term(
    effect: str,
    *,
    entering: bool,
    duration_seconds: float,
    window_seconds: float,
    intensity: float,
) -> tuple[str, str] | None:
    if effect == "Rise":
        dimension = "H"
        distance = 0.08 * intensity
        axis = "y"
    elif effect in {"Pan", "Drift"}:
        dimension = "W"
        distance = 0.06 * intensity
        axis = "x"
    else:
        return None

    window = f"{window_seconds:.6f}"
    distance_expr = f"{dimension}*{distance:.6f}"
    if entering:
        expression = f"if(lt(t,{window}),(1-t/{window})*{distance_expr},0)"
    else:
        exit_start = max(0.0, duration_seconds - window_seconds)
        start = f"{exit_start:.6f}"
        expression = (
            f"if(gt(t,{start}),((t-{start})/{window})*{distance_expr},0)"
        )
    return axis, expression


def _combine(base: str, terms: list[str]) -> str:
    if not terms:
        return base
    return f"({base})+" + "+".join(f"({term})" for term in terms)


def compile_motion_overlay_position(
    *,
    base_x: str,
    base_y: str,
    assignment: AnimationAssignment | None,
    duration_seconds: float,
) -> tuple[str, str]:
    """Compile render-safe per-asset motion into overlay x/y expressions."""

    if not assignment_has_native_motion(assignment) or assignment is None:
        return base_x, base_y

    duration = max(0.001, duration_seconds)
    window = min(0.25, duration / 2.0)
    intensity = max(0.0, min(2.0, assignment.intensity))
    x_terms: list[str] = []
    y_terms: list[str] = []

    for effect, entering in (
        (assignment.enter_effect, True),
        (assignment.exit_effect, False),
    ):
        compiled = _motion_term(
            effect,
            entering=entering,
            duration_seconds=duration,
            window_seconds=window,
            intensity=intensity,
        )
        if compiled is None:
            continue
        axis, expression = compiled
        if axis == "x":
            x_terms.append(expression)
        else:
            y_terms.append(expression)

    return _combine(base_x, x_terms), _combine(base_y, y_terms)
