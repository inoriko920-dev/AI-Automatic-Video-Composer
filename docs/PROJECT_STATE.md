# PROJECT_STATE — Post STEP 15 / Release 0.1.1

- Factory Steps: 00–15 complete
- Status: PASS
- Current release: `0.1.1`
- GitHub Release publication: **PUBLISHED / VERIFIED**
- Git tag: `v0.1.1`
- Frozen release source: `release/0.1.1` @ `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`
- Canonical maintenance release workflow: `Maintenance Release Windows 0.1.1` run `#1` / `37181599863`
- Published maintenance line: `0.1.x`
- Active source line: **0.2 completion source / Windows test build verified / not yet published**
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

Branch `main` contains maintenance and the completed **0.2 completion wave (#260)** created after frozen release `v0.1.1`. These capabilities have been verified in a fresh Windows portable **test build**, but they are still not part of the published `v0.1.1` GitHub Release.

Current 0.2 completion source includes:
- secure Gemini credential management from PR #251 with deterministic slots `1–100`, Windows Credential Manager storage, and no plaintext fallback;
- real microphone narration recording from PR #262, producing WAV and binding it to `narration_audio` through project history;
- bounded live Gemini Auto (AI) from PR #264, restricted to validated native render-backed animation assignments and one-step Undo;
- background render and Gemini execution from PR #266 using the canonical `JobManager`, with overlapping work rejected and stale Gemini results discarded;
- completion cleanup from #267: unsupported GPU/Advanced export controls are not advertised, reference-only AI Agent/empty tabs are removed from live runtime surfaces, obsolete read-only subtitle actions are hidden, and Home/New Project no longer present fake project/history controls;
- Gemini transport hardening from #271/#272: the selected raw API key is sent in the `x-goog-api-key` request header rather than being embedded in the request URL.

Raw API-key values remain outside `ProjectState`, project files, logs, and status diagnostics. FFmpeg/ffprobe remain external dependencies.

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
No runtime blocker is known for normal `0.1.x` maintenance. Repository administration still has #20 (branch protection), which requires owner/admin access.

## 0.2 COMPLETION TEST BUILD

The approved 0.2 completion wave (#260) has completed its source/runtime scope and fresh Windows test-build gate.

Final verified 0.2 application source after cleanup #274:
- application source: `main` @ `2efd414b6a582b86d39c5b6d1f7d4ff7d0bb6897`;
- post-merge CI run `37420784262`: **PASS**;
- post-merge CodeQL run `37420784256`: **PASS**;
- seven unreferenced deferred source stubs were retired without changing user-visible runtime behavior;
- architecture/data-flow documentation now matches the live Qt preview and external FFmpeg contract.

Final Windows test packaging after #274 cleanup:
- workflow: **Package Windows Foundation**;
- run: `37420955954`;
- build branch commit: `60345bc140cfa8a47e0e718c1d792c640da45431`;
- branch differed from final application source `2efd414b6a582b86d39c5b6d1f7d4ff7d0bb6897` only by the one-off workflow push trigger; no application source file differed;
- PyInstaller onedir: **PASS**;
- portable verification: **PASS**;
- verification markers: `PORTABLE_SMOKE_OK`, `FFMPEG_SLOT_OK`, `FINAL_RELEASE_DOCS_OK`;
- Actions artifact: `AAVC-foundation-win64` / artifact ID `11392374584`;
- uploaded artifact wrapper digest: `sha256:0fc80d64e1a022dd2c4530c89186316217ae1ad0d062eb1bbd39520139a1e221`;
- extracted portable ZIP SHA-256: `a59737cd2cf5766eb3c2b7c76d2c549dbbb435f1db7ad84683efd3d7489d7802`;
- portable ZIP contains root `AI Automatic Video Composer.exe` and `tools/ffmpeg/README.md`;
- redundant `_internal/tools/ffmpeg/README.md` is absent.

This is a **test build**, not a new published GitHub Release. Published `v0.1.1` remains frozen and unchanged.

## ACTIVE TASK
No technical implementation or cleanup task is active. **#260 and #274 are complete.** Project license decision #27 is resolved as **MIT** with root `LICENSE`, SPDX package metadata, and provenance documentation. Remaining repository administration item #20 (branch protection) requires owner/admin access.

## NEXT EXACT ACTION
User performs direct end-to-end testing of the final 0.2 Windows portable ZIP on the target PC. Any concrete runtime defect should be handled as a focused bug/compatibility task without reopening completed STEP 09–15 planning or expanding into the separate arbitrary-video/multitrack experiment.
