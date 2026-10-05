# PROJECT_STATE — Post STEP 15 / Release 0.1.1

- Factory Steps: 00–15 complete
- Status: PASS
- Current release: `0.1.1`
- GitHub Release publication: **PUBLISHED / VERIFIED**
- Git tag: `v0.1.1`
- Frozen release source: `release/0.1.1` @ `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`
- Canonical maintenance release workflow: `Maintenance Release Windows 0.1.1` run `#1` / `37181599863`
- Maintenance line: `0.1.x`
- Architecture: ARCH-AAVC-v1.0
- Product Blueprint: PB-AAVC-v1.0
- UI Freeze: UIF-AAVC-v1.0
- Code Constitution: CC-AAVC-v1.0
- Repository: `inoriko920-dev/AI-Automatic-Video-Composer`
- Primary branch: `main`

## IMPLEMENTED
Production source, UI, end-to-end composition flow, external/provider integration, hardening/QA, Windows portable packaging, release-candidate gate, final-release gate, backup/recovery policy, maintenance policy, and guarded GitHub Release publishing are implemented through STEP 15 and the 0.1.x maintenance line.

Maintenance release `0.1.1` fixes issue #9 without adding a new product feature wave:
- the app-local FFmpeg slot is now physically `tools/ffmpeg/` beside `AI Automatic Video Composer.exe`;
- portable verification requires that exact root slot;
- the redundant `_internal/tools/ffmpeg/README.md` packaging path is removed;
- package/runtime version metadata is aligned with `0.1.1`.

FFmpeg and ffprobe remain external dependencies and are not redistributed by AAVC.

### Post-release maintenance on `main`

Branch `main` contains maintenance and editor/runtime improvements created after the frozen `v0.1.1` release. These changes are source-state capabilities and must not be described as already present in the published `v0.1.1` binary until a later build/release is produced.

Current post-release source includes secure Gemini credential management from PR #251:
- menu **AI → Status Gemini…** reports only configured slot numbers/count;
- **Simpan / Ganti API Key Gemini…** writes a selected slot through Windows Credential Manager;
- **Hapus API Key Gemini…** removes a selected credential after confirmation;
- deterministic credential slots `1–100` are supported;
- raw API-key values are not stored in `ProjectState`, project files, logs, or status diagnostics and are not displayed back to the user;
- no plaintext credential fallback is provided on unsupported platforms;
- this credential-management layer does **not** yet make a live Gemini request or apply AI mutations to a project.

## VERIFIED
Official GitHub Release `v0.1.1` is published and targets frozen source commit `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`.

Canonical release run `37181599863` passed:
- frozen-source resolution and version validation;
- compileall;
- Ruff;
- strict mypy;
- cheap pytest;
- STEP 09 Qt screenshot capture/verification;
- PyInstaller Windows onedir build;
- portable smoke/content verification;
- release-bundle preparation and Actions artifact upload;
- existing tag/release overwrite guard;
- GitHub Release publication.

Published ZIP integrity:
- Windows ZIP SHA-256: `84ad8cc93f055cb95fc2624511a9eecd541505627628090c277a048e5e8495b4`
- Source ZIP SHA-256: `a5a00b196e76d34684deef97b9dc605b748e1a32f2f92fe6f761c25b13f720bb`

Independent artifact inspection confirmed:
- `AI Automatic Video Composer.exe` exists at portable root;
- `tools/ffmpeg/README.md` exists at portable root;
- `_internal/tools/ffmpeg/README.md` is absent;
- `BUILD_INFO.txt` records version `0.1.1` and the same frozen commit;
- `SHA256SUMS.txt` matches both published ZIP hashes.

A duplicate publication attempt was blocked by the overwrite guard after `v0.1.1` already existed; no published tag or asset was replaced.

## PUBLISHED HISTORY
- `v0.1.0` remains the immutable original final-release baseline at commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.
- `v0.1.1` is the current maintenance release at commit `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`.

## PROVISIONAL / EXTERNAL WATCH
No factory blocker remains. Before later patch releases, re-check compatibility when Gemini/provider behavior, PySide6/Qt, Python 3.12 support, FFmpeg capability/license profile, or Windows 11 packaging/runtime behavior changes.

## BLOCKERS
None known for normal `0.1.x` maintenance.

## ACTIVE TASK
No release or feature task is currently active. `REL-0.1.0-PUBLISH` and `REL-0.1.1-PUBLISH` are complete.

## NEXT EXACT ACTION
Wait for a concrete bug report, compatibility issue, security hardening need, packaging issue, or explicitly approved new capability.

Classify later changes under `MAINTENANCE.md` before implementation:
- bug/compatibility/security/packaging fix -> patch `0.1.x`;
- new compatible user-visible capability -> next minor release;
- breaking schema/workflow change -> major-version planning.

Do not restart completed STEP 09–15 work unless regression evidence requires it.
