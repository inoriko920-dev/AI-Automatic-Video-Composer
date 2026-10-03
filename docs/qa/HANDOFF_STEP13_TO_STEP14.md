# HANDOFF — STEP 13 → STEP 14

## Entry condition for STEP 14
- STEP 09 PASS.
- STEP 10 PASS.
- STEP 11 PASS.
- STEP 12 PASS.
- STEP 13 final Windows CI PASS on the closing SHA.

## Frozen technical baseline
- Python 3.12 x64.
- PySide6 / Qt Widgets.
- Modular monolith.
- deterministic ProjectState + FFmpeg render boundary.
- ASS/libass subtitle pipeline.
- provider-neutral AI boundary with Gemini adapter.
- Windows Credential Manager production secret storage.
- sticky active provider credential; no quota/rate-limit credential hopping.
- diagnostics/redaction/support bundle.
- cancellable background jobs.
- render preflight/output validation.

## STEP 14 first tasks
1. Create `release/step14-rc1` from the exact STEP 13 closing SHA.
2. Set an RC identity/version and record source SHA.
3. Upgrade the Windows package workflow from “foundation” to exact RC packaging.
4. Produce file manifest, SHA-256 checksum and build provenance.
5. Extract the produced ZIP into a fresh folder and run packaged smoke tests there.
6. Add candidate hygiene/security scan.
7. Record RC test evidence and only then mark STEP 14 PASS.

## Explicit non-goals
Do not silently merge new features into the RC. Any release-blocking defect returns to a scoped fix + full regression run.
