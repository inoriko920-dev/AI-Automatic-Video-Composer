# STEP 09 — App Shell / UI Implementation

Status: RUNTIME_SCREENSHOT_CAPTURE_PASS / VISUAL_PARITY_IN_PROGRESS

Implemented:
- Canonical light white/blue design tokens.
- Canonical menu and 48px editor toolbar.
- Resizable editor shell: left Scene/Aset, center preview, right inspector, bottom timeline,
  and status area.
- Presentation routes for UI-002, UI-003, UI-010, UI-013, UI-014, UI-027, UI-035, UI-041.
- Representative Home, New Project DOCX, SINGLE, DOUBLE, Subtitle, Export and Validation UI.
- Windows CI capture of all 8 representative 1920x1080 Qt states.
- Explicit Windows font registration for stable offscreen screenshot text rendering.
- CI verifies exactly 8 screenshot PNGs and uploads `step09-ui-actual` as build evidence.
- Pure geometry acceptance tests for 1920x1080 and compact desktop.

Evidence:
- CI run #26 captured and uploaded all 8 actual screenshots successfully.
- Compile, Ruff, strict mypy, cheap pytest, capture, screenshot verification, and artifact upload
  all passed on the Windows runner.

Visual parity remains IN PROGRESS:
- Runtime screenshot production is now proven.
- UI-002 and UI-003 are being aligned to their frozen STEP 04 references.
- UI-035 capture now composes the export modal over the editor.
- UI-041 capture now composes the validation surface at the right side of the editor.
- Formal STEP 09 PASS is not claimed until representative screenshots are reviewed against
  the canonical frozen UI references.

UI freeze source correction:
- Canonical STEP 04 source set is UI-001 through UI-042, not UI-047.
