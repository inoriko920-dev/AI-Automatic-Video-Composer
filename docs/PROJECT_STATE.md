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
- Gemini transport hardening from #271/#272: the selected raw API key is sent in the `x-goog-api-key` request header rather than being embedded in the request URL;
- atomic render output from #278/#279 so failed FFmpeg work cannot clobber a previously valid output;
- tolerant external-process output decoding from #282/#283 so invalid tool bytes cannot crash the Python decode boundary;
- final stability hardening from #280/#285/#287/#289 via #290: narration records to staging before atomic replacement, unsupported future project schemas are refused, malformed DOCX XML becomes a safe import error, and application close is blocked while Render/Auto AI work is active;
- SRT import hardening from #292/#293: empty, structurally malformed, or invalid-timing subtitle sources are rejected before ProjectState mutation;
- Windows credential hardening from #295/#296: corrupt Credential Manager blobs are normalized into safe credential errors instead of leaking raw Unicode decode exceptions;
- subtitle render staging hardening from #298/#299: full/selection export use unique temporary ASS intermediates that are always cleaned and never overwrite a user-owned sidecar ASS.

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

## 0.2 STABILITY-HARDENED TEST BUILD

The approved 0.2 completion scope is complete and has undergone focused stability audits. The latest runtime source is verified by CI, CodeQL, regression tests, STEP09 visual checks, and a fresh Windows portable packaging gate.

Stability-hardened runtime source:
- application source: `main` @ `d520b7afd975902ee3d2068a70a5fdcfc07957aa`;
- post-merge CI run `37431110423`: **PASS**;
- post-merge CodeQL run `37431110449`: **PASS**.

Additional stability fixes:
- #278/#279 — render output is staged and atomically finalized; failed renders preserve existing destination files;
- #282/#283 — external-process stdout/stderr decoding tolerates invalid Windows/tool bytes;
- #280/#290 — narration recording uses staging and never deletes/replaces an existing WAV until the new recording is valid;
- #285/#290 — project files with unsupported future schema versions are rejected instead of silently loaded;
- #287/#290 — malformed DOCX XML is converted into a safe AAVC import error;
- #289/#290 — the app refuses to close while Render/Auto AI background work is active so the GUI event loop is not removed from a running job;
- #292/#293 — empty, structurally malformed, or invalid-timing SRT files are rejected before subtitle source mutation;
- #295/#296 — corrupt Windows Credential Manager blobs are converted into safe credential read failures instead of raw Unicode decode exceptions;
- #298/#299 — subtitle burn-in uses unique temporary ASS staging for both full and selection export; intermediates are always cleaned and user-owned sidecar ASS files are preserved.

Latest Windows stability test packaging:
- workflow: **Package Windows Foundation**;
- run: `37431186070`;
- build branch commit: `e8281b4c8dd213a2e1d1102b3ab6c483bd22914b`;
- build branch differed from runtime source only by the one-off workflow push trigger; no application source file differed;
- PyInstaller onedir: **PASS**;
- portable verification: **PASS**;
- verification markers: `PORTABLE_SMOKE_OK`, `FFMPEG_SLOT_OK`, `FINAL_RELEASE_DOCS_OK`;
- Actions artifact: `AAVC-foundation-win64` / artifact ID `11396354889`;
- uploaded artifact wrapper digest: `sha256:d2fdb1c6b36db78a5248d237fda52485980b48b3ac2c93f5d7d23f1a49f0c7ec`;
- extracted portable ZIP SHA-256: `93042ce86e317453a5e1b88b3e1685d222425e33b461b5419768b805516b50e3`;
- extracted portable ZIP size: `62096463` bytes / 268 entries;
- root `AI Automatic Video Composer.exe` present;
- root `tools/ffmpeg/README.md` present;
- redundant `_internal/tools/ffmpeg/README.md` absent;
- no `.aavc-subtitle-*.ass` staging file is bundled.

This is a **test build**, not a new published GitHub Release. Published `v0.1.1` remains frozen and unchanged.

## ACTIVE TASK
No known technical implementation or automated-stability task is active. Completion #260, cleanup #274, MIT licensing #27, and stability issues #278/#280/#282/#285/#287/#289/#292/#295/#298 are complete. Remaining repository administration item #20 (branch protection) requires owner/admin access.

## NEXT EXACT ACTION
Run direct end-to-end testing of the stability-hardened Windows portable ZIP on the target Windows PC. Automated/build gates are green, but production stability cannot be proven without real runtime use. Any concrete runtime defect should be handled as a focused bug/compatibility task without reopening completed STEP 09–15 planning or expanding product scope.
