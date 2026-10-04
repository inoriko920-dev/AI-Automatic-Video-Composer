from __future__ import annotations

from aavc.bootstrap.composition_root import FoundationServices
from aavc.presentation.native_motion_playback import install_native_motion_preview
from aavc.presentation.navigation import UiRoute
from aavc.presentation.timeline_preview_seek import install_timeline_preview_seek
from aavc.presentation.windows.native_motion_window import NativeMotionMainWindow


class NativeMotionPreviewMainWindow(NativeMotionMainWindow):
    """Native-motion editor with non-destructive selected-scene playback preview."""

    def refresh_editor_overview(self) -> None:
        super().refresh_editor_overview()
        project = self.services.project_session.current
        if project is None:
            return
        root = self._route_widgets.get(UiRoute.EDITOR)
        if root is not None:
            install_native_motion_preview(root, project)
            install_timeline_preview_seek(root, project)


def create_native_motion_preview_main_window(
    services: FoundationServices,
    initial_state: str = "UI-002",
) -> NativeMotionPreviewMainWindow:
    return NativeMotionPreviewMainWindow(services, initial_state=initial_state)
