from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from aavc.presentation.widgets.editor_shell import create_editor_shell
from aavc.presentation.widgets.live_subtitle import create_live_subtitle_inspector


def create_live_subtitle_screen(
    source: str | Path,
    *,
    on_reload: Callable[[], None] | None = None,
) -> Any:
    parts = create_editor_shell("subtitle")
    inspector = create_live_subtitle_inspector(source, on_reload=on_reload)

    parts.right_tabs.removeTab(0)
    parts.right_tabs.insertTab(0, inspector, "Subtitle")
    parts.right_tabs.setCurrentIndex(0)
    return parts.root
