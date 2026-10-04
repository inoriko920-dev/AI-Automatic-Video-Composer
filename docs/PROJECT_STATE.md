# PROJECT_STATE — Maintenance Release 0.1.1

- Factory Steps: 00–15 complete
- Status: PASS / maintenance patch release preparation
- Last published release: `0.1.0`
- Maintenance release candidate: `0.1.1`
- 0.1.1 source branch: `release/0.1.1`
- Maintenance line: `0.1.x`
- Architecture: ARCH-AAVC-v1.0
- Product Blueprint: PB-AAVC-v1.0
- UI Freeze: UIF-AAVC-v1.0
- Code Constitution: CC-AAVC-v1.0
- Repository: `inoriko920-dev/AI-Automatic-Video-Composer`
- Primary branch: `main`

## PUBLISHED BASELINE — 0.1.0
Official GitHub Release `v0.1.0` is published and verified. It targets frozen release commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.

Published 0.1.0 ZIP integrity:
- Windows ZIP SHA-256: `c3e4f92656aefd3d57329627c52b8e057d2f8cac5a0a757471b90cb1d68915e8`
- Source ZIP SHA-256: `1264b1dc483932b496acf87dee21c93f92d4e1b222aa37ca2284fbf99b9df328`

## 0.1.1 MAINTENANCE PATCH
0.1.1 contains no new product feature wave. It fixes maintenance issue #9:
- restore `tools/ffmpeg/` beside the portable EXE as the real app-local FFmpeg slot;
- require that exact portable structure during verification;
- remove the redundant PyInstaller-internal FFmpeg guide copy;
- align package/runtime version metadata with the maintenance release.

FFmpeg/ffprobe remain external dependencies and are not redistributed by AAVC.

## VERIFIED BEFORE RELEASE
The maintenance fix passed normal CI on `main` and an independent Windows packaging validation. The validation artifact physically contained:
- `AI Automatic Video Composer.exe` at portable root;
- `tools/ffmpeg/README.md` at portable root;
- no `_internal/tools/ffmpeg/README.md` duplicate.

The `release/0.1.1` branch must pass its final CI and the dedicated 0.1.1 release workflow before publication.

## BLOCKERS
No known code blocker. Publication remains pending until the frozen 0.1.1 release gate completes successfully.

## ACTIVE TASK
`REL-0.1.1-PUBLISH` — validate, freeze, and publish official GitHub Release `v0.1.1` without modifying `v0.1.0`.

## NEXT EXACT ACTION
1. Complete CI on `release/0.1.1`.
2. Freeze the resulting release commit.
3. Run `Maintenance Release Windows 0.1.1` from the guarded publish path.
4. Verify tag target, release assets, `BUILD_INFO.txt`, and SHA-256 values.
5. Synchronize `main` and close `REL-0.1.1-PUBLISH`.

Do not restart completed STEP 09–15 work unless regression evidence requires it.
