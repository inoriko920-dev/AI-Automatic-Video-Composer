# STEP 13 — PORTABLE QA

Status: **PROVISIONAL — STEP 14 owns the exact Release Candidate package.**

## Already available
- PyInstaller onedir packaging specification exists.
- Windows packaging workflow exists and can build a portable foundation artifact.
- `scripts/verify_portable.ps1` exists as the current packaging smoke boundary.
- Source CI is green on Windows and real Qt UI capture works.

## Not claimed by STEP 13
STEP 13 does not claim that an exact RC ZIP has been:
- named/versioned as a release candidate;
- extracted into a clean destination and launched from the extracted copy;
- checked against a file manifest + SHA-256 checksum;
- checked for secret/debug/cache/source contamination;
- tied to one immutable candidate SHA with provenance;
- validated with the approved FFmpeg binary/capabilities/license profile.

## Required STEP 14 portable gate
1. Freeze RC version and source SHA.
2. Build PyInstaller onedir on Windows.
3. Create candidate ZIP from that exact build.
4. Generate manifest + SHA-256 + provenance.
5. Extract ZIP to a fresh folder.
6. Launch/smoke the extracted app, not the build tree.
7. Verify required Qt plugins/resources and expected project path behavior.
8. Run hygiene/security scan for secrets, debug artifacts, caches and unintended local paths.
9. Record PASS/FAIL evidence before promotion.
