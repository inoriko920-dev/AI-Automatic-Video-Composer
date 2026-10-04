from __future__ import annotations

from aavc.domain.project.models import AnimationAssignment

NATIVE_VISUAL_MOTION_EFFECTS = frozenset({"Rise", "Pan", "Drift"})
NATIVE_VISUAL_ALPHA_EFFECTS = frozenset({"Fade", "Pop"})
NATIVE_VISUAL_SCALE_EFFECTS = frozenset({"Pop"})
NATIVE_VISUAL_EFFECTS = (
    NATIVE_VISUAL_MOTION_EFFECTS
    | NATIVE_VISUAL_ALPHA_EFFECTS
    | NATIVE_VISUAL_SCALE_EFFECTS
)


def is_native_visual_motion_effect(name: str) -> bool:
    return name in NATIVE_VISUAL_MOTION_EFFECTS


def is_native_visual_alpha_effect(name: str) -> bool:
    return name in NATIVE_VISUAL_ALPHA_EFFECTS


def is_native_visual_scale_effect(name: str) -> bool:
    return name in NATIVE_VISUAL_SCALE_EFFECTS


def is_native_visual_effect(name: str) -> bool:
    return name in NATIVE_VISUAL_EFFECTS


def assignment_has_native_motion(
    assignment: AnimationAssignment | None,
) -> bool:
    if assignment is None or assignment.intensity <= 0:
        return False
    return (
        is_native_visual_motion_effect(assignment.enter_effect)
        or is_native_visual_motion_effect(assignment.exit_effect)
    )


def assignment_has_native_alpha(
    assignment: AnimationAssignment | None,
) -> bool:
    if assignment is None or assignment.intensity <= 0:
        return False
    return (
        is_native_visual_alpha_effect(assignment.enter_effect)
        or is_native_visual_alpha_effect(assignment.exit_effect)
    )


def assignment_has_native_scale(
    assignment: AnimationAssignment | None,
) -> bool:
    if assignment is None or assignment.intensity <= 0:
        return False
    return (
        is_native_visual_scale_effect(assignment.enter_effect)
        or is_native_visual_scale_effect(assignment.exit_effect)
    )


def compile_native_alpha_filters(
    assignment: AnimationAssignment | None,
    *,
    duration_seconds: float,
) -> tuple[str, ...]:
    """Compile render-safe per-asset alpha transitions for native alpha effects."""

    if not assignment_has_native_alpha(assignment) or assignment is None:
        return ()

    duration = max(0.001, float(duration_seconds))
    window = min(0.25, duration / 2.0)
    filters: list[str] = ["format=rgba"]
    if is_native_visual_alpha_effect(assignment.enter_effect):
        filters.append(f"fade=t=in:st=0:d={window:.6f}:alpha=1")
    if is_native_visual_alpha_effect(assignment.exit_effect):
        exit_start = max(0.0, duration - window)
        filters.append(
            f"fade=t=out:st={exit_start:.6f}:d={window:.6f}:alpha=1"
        )
    return tuple(filters)


def _native_scale_factor(
    assignment: AnimationAssignment,
    *,
    duration_seconds: float,
) -> str:
    duration = max(0.001, float(duration_seconds))
    window_seconds = min(0.25, duration / 2.0)
    window = f"{window_seconds:.6f}"
    exit_start_seconds = max(0.0, duration - window_seconds)
    exit_start = f"{exit_start_seconds:.6f}"
    has_enter = is_native_visual_scale_effect(assignment.enter_effect)
    has_exit = is_native_visual_scale_effect(assignment.exit_effect)

    enter_expr = f"0.85+0.15*t/{window}"
    exit_expr = f"1-0.15*(t-{exit_start})/{window}"
    if has_enter and has_exit:
        return (
            f"if(lt(t,{window}),{enter_expr},"
            f"if(gt(t,{exit_start}),{exit_expr},1))"
        )
    if has_enter:
        return f"if(lt(t,{window}),{enter_expr},1)"
    if has_exit:
        return f"if(gt(t,{exit_start}),{exit_expr},1)"
    return "1"


def compile_native_scale_filter(
    assignment: AnimationAssignment | None,
    *,
    duration_seconds: float,
) -> str | None:
    """Compile frame-evaluated per-asset scale for native Pop assignments."""

    if not assignment_has_native_scale(assignment) or assignment is None:
        return None

    factor = _native_scale_factor(
        assignment,
        duration_seconds=duration_seconds,
    )
    width = f"max(2,trunc(iw*({factor})/2)*2)"
    return f"scale=w='{width}':h=-2:eval=frame"


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
