# STEP 09 — App Shell / UI Implementation

Status: CODE_IMPLEMENTED / RUNTIME_SCREENSHOT_GATE_PENDING

Implemented:
- Canonical light white/blue design tokens.
- Canonical menu and 48px toolbar.
- Resizable editor shell: left Scene/Aset, center preview, right inspector, bottom timeline, status.
- Presentation-only route catalog for UI-002, UI-003, UI-010, UI-013, UI-014, UI-027, UI-035, UI-041.
- Representative Home, New Project DOCX, SINGLE, DOUBLE, Subtitle, Export and Validation UI.
- Capture CLI and capture script for actual 1920x1080 Qt screenshots.
- Pure geometry acceptance tests for 1920x1080 and compact desktop.

Not claimed as complete evidence in this container:
- PySide6 is not installed in the execution container and network install is unavailable.
- Therefore actual Qt screenshots cannot be captured here without falsifying evidence.
- Run `python scripts/capture_step09_ui.py` on the pinned Windows/CI runtime after installing locked dependencies.
