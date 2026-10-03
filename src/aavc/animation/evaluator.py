from __future__ import annotations

from dataclasses import dataclass

from .registry import validate_effect


@dataclass(frozen=True, slots=True)
class TransformDelta:
    opacity: float = 1.0
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0


def evaluate_effect(name: str, progress: float, *, entering: bool = True) -> TransformDelta:
    """Evaluate a small canonical primitive subset for preview/render adapters.

    Product effects remain registry-level identities. This evaluator intentionally provides
    conservative primitives so layout ownership stays separate from animation deltas.
    """
    validate_effect(name)
    p = max(0.0, min(1.0, progress))
    if not entering:
        p = 1.0 - p
    if name == "Fade":
        return TransformDelta(opacity=p)
    if name in {"Pop", "Stomp"}:
        return TransformDelta(opacity=p, scale=0.85 + 0.15 * p)
    if name in {"Rise", "Slide Up"}:
        return TransformDelta(opacity=p, offset_y=(1.0 - p) * 0.08)
    if name in {"Pan", "Drift"}:
        return TransformDelta(opacity=p, offset_x=(1.0 - p) * 0.06)
    if name == "Breathe":
        return TransformDelta(opacity=1.0, scale=0.98 + 0.02 * p)
    return TransformDelta(opacity=p)
