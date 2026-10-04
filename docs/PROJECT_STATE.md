# PROJECT_STATE — Post STEP 15 / Release 0.1.0

- Factory Steps: 00–15 complete
- Status: PASS
- Current release: `0.1.0`
- GitHub Release publication: **PUBLISHED / VERIFIED**
- Git tag: `v0.1.0`
- Frozen release source: `release/0.1.0` @ `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Final publish workflow: `Final Release Windows` run `#6` / `37180132492`
- Maintenance line: `0.1.x`
- Architecture: ARCH-AAVC-v1.0
- Product Blueprint: PB-AAVC-v1.0
- UI Freeze: UIF-AAVC-v1.0
- Code Constitution: CC-AAVC-v1.0
- Repository: `inoriko920-dev/AI-Automatic-Video-Composer`
- Primary branch: `main`

## IMPLEMENTED
Production source, UI, end-to-end composition flow, external/provider integration, hardening/QA, Windows portable packaging, release-candidate gate, final-release gate, backup/recovery policy, maintenance policy, and guarded GitHub Release publishing workflow are implemented through STEP 15 and post-release maintenance.

See `README.md`, `STEP15_STATUS.md`, `FINAL_RELEASE_MANIFEST.md`, and `docs/RELEASE_PUBLISHING.md` for the canonical capability, release, and publishing summary.

## VERIFIED
The official GitHub Release `v0.1.0` is published and targets the frozen release commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.

Final publication run `37180132492` passed:
- release-input validation;
- frozen-source resolution;
- compileall;
- Ruff;
- strict mypy;
- cheap pytest;
- STEP 09 Qt screenshot capture/verification;
- PyInstaller Windows onedir build;
- portable smoke/content verification;
- release-bundle preparation;
- Actions artifact upload;
- existing tag/release overwrite guard;
- GitHub Release publication.

Published ZIP integrity:
- Windows ZIP SHA-256: `c3e4f92656aefd3d57329627c52b8e057d2f8cac5a0a757471b90cb1d68915e8`
- Source ZIP SHA-256: `1264b1dc483932b496acf87dee21c93f92d4e1b222aa37ca2284fbf99b9df328`

`BUILD_INFO.txt` records release commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5` and version `0.1.0`. `SHA256SUMS.txt` matches independently computed hashes for both ZIP files.

## PROVISIONAL / EXTERNAL WATCH
No factory blocker remains. Before patch releases, re-check compatibility when Gemini/provider behavior, PySide6/Qt, Python 3.12 support, FFmpeg capability/license profile, or Windows 11 packaging/runtime behavior changes.

## BLOCKERS
None known for normal `0.1.x` maintenance.

## ACTIVE TASK
No release or feature task is currently active. `REL-0.1.0-PUBLISH` is complete.

## NEXT EXACT ACTION
Wait for a concrete bug report, compatibility issue, security hardening need, packaging issue, or explicitly approved new capability.

Classify later changes under `MAINTENANCE.md` before implementation:
- bug/compatibility/security/packaging fix -> patch `0.1.x`;
- new compatible user-visible capability -> next minor release;
- breaking schema/workflow change -> major-version planning.

Do not restart completed STEP 09–15 work unless regression evidence requires it.
