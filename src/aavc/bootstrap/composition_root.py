from __future__ import annotations

from dataclasses import dataclass
from aavc.platform.paths import PathService

@dataclass(frozen=True, slots=True)
class FoundationServices:
    app_name: str
    paths: PathService


def build_foundation_services() -> FoundationServices:
    return FoundationServices(
        app_name="AI Automatic Video Composer",
        paths=PathService.discover(),
    )
