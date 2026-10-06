# ACTIVE TASKS — Post Release 0.1.1

## ASTRA maintenance audit — 2026-10-06
Status: **IN PROGRESS** on branch `sol/astra-aavc-bugfix-2026-10-06`.

Active findings:
- AAVC-ASTRA-01 (P1): reject structurally invalid project/recovery payloads before state/file mutation.
- AAVC-ASTRA-02 (P1): move large FFmpeg filter graph off the Windows command line and preflight argv length.
- AAVC-ASTRA-03 (P2): make ASS subtitle path escaping robust for apostrophes and legal target paths.
- AAVC-ASTRA-04 (P2): make preview timing follow a monotonic elapsed clock rather than callback count.
- AAVC-ASTRA-05 (P2): split Pause from Stop/reset so pause/resume preserves playhead.

Canonical implementation plan: `docs/audits/2026-10-06-astra/AUDIT_PLAN.md`.
Do not mark these complete until their regression tests and environment-specific gates pass.

## Current queue
No known technical implementation or automated-stability task is active. Completion #260, cleanup #274, project license #27, and focused stability hardening issues #278/#280/#282/#285/#287/#289/#292/#295 are complete. The only remaining repository administration item is #20 (branch protection), which requires owner/admin access.

Software Factory STEP 00–15 remains complete and published `v0.1.1` stays frozen. The explicitly approved 0.2 completion wave has completed its source and Windows test-build gate.

### 0.2 completion wave — #260
Status: **COMPLETE**

Completed runtime work:
- project/File/Export action-state synchronization (#258/#259);
- real microphone narration workflow (#261/#262);
- bounded live Gemini Auto (AI) using secure credential slots (#263/#264);
- responsive background render/Gemini work through canonical JobManager (#265/#266);
- visible-placeholder cleanup and documentation synchronization (#267);
- post-merge CI and CodeQL on completed `main`: PASS;
- fresh Windows portable test build: PASS;
- portable smoke/content verification: PASS.

Latest stability-hardened 0.2 build evidence:
- runtime application source `9ce7d3c3125947c69e7dcf357f6ecbbc6707fee7`;
- CI run `37429362040`: PASS;
- CodeQL run `37429362044`: PASS;
- packaging run `37429446908`: PASS;
- Actions artifact ID `11396573064`;
- artifact wrapper SHA-256 `e801c879a5efd1f95da555777f035b5fe554c52dcef5dfa1f46a8a8345269862`;
- portable ZIP SHA-256 `6d9f3d57dd5c8ba47a18bb65a56e5c26ce8cac1962bacfee0ffff8c9efdfbe52`.

### Stability hardening — #278 / #280 / #282 / #285 / #287 / #289 / #292 / #295
Status: **COMPLETE**

Completed:
- atomic FFmpeg output finalization preserves prior valid output on render failure;
- external-process output decoding cannot fail on undecodable bytes;
- narration recording stages output and preserves an existing WAV on cancel/error;
- unsupported future project schemas are refused before session mutation;
- malformed DOCX XML is surfaced as a controlled import error;
- application close is blocked while Render/Auto AI background work is active;
- empty/malformed/invalid-timing SRT imports are rejected before project mutation;
- corrupt Windows Credential Manager blobs are normalized into safe errors;
- focused regression tests added for each behavior;
- final combined PR #290 CI + CodeQL: PASS;
- merged runtime source CI + CodeQL: PASS;
- fresh Windows portable packaging and smoke/content verification: PASS.

### Final technical cleanup — #274
Status: **COMPLETE**

Completed:
- removed seven source modules/files that only represented unreferenced deferred-owner placeholders;
- corrected stale architecture/data-flow claims about bundled FFmpeg and proxy/PlaybackClock preview;
- preserved all user-visible 0.2 behavior;
- PR #275 CI + CodeQL: PASS;
- merged `main` CI + CodeQL: PASS;
- fresh Windows portable build from the cleaned runtime source: PASS;
- portable smoke/content verification: PASS.

Next action is direct end-to-end Windows testing of the stability-hardened portable build. New capability work still requires explicit approval.


### REL-0.1.1-PUBLISH — Publish maintenance patch
Status: **COMPLETE**

Official GitHub Release `v0.1.1` was published successfully from frozen source `release/0.1.1`, commit `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`.

Verified evidence:
- Canonical release workflow: `Maintenance Release Windows 0.1.1` run `#1` / `37181599863`
- Tag: `v0.1.1`
- Release target commit: `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`
- Windows ZIP SHA-256: `84ad8cc93f055cb95fc2624511a9eecd541505627628090c277a048e5e8495b4`
- Source ZIP SHA-256: `a5a00b196e76d34684deef97b9dc605b748e1a32f2f92fe6f761c25b13f720bb`
- `BUILD_INFO.txt` records version `0.1.1` and the same frozen commit.
- `SHA256SUMS.txt` matches independently computed hashes for both release ZIP files.
- Direct ZIP inspection confirmed root `tools/ffmpeg/README.md` and no `_internal/tools/ffmpeg/README.md` duplicate.
- Maintenance issue #9 is closed.

A second one-shot publication attempt was blocked by the overwrite guard after the release already existed. No existing tag/release was replaced.

### REL-0.1.0-PUBLISH — Publish original final release
Status: **COMPLETE**

Official GitHub Release `v0.1.0` remains the immutable original baseline at commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.

## Maintenance intake checklist
When a concrete request arrives:
1. record the symptom or requested capability and expected behavior;
2. search existing implementation/tests before creating modules;
3. classify patch/minor/major impact using `MAINTENANCE.md`;
4. identify affected architecture/UI/schema/provider/packaging contracts;
5. define focused implementation and regression-test tasks;
6. run the required gates and preserve evidence;
7. update this file with active task IDs while work is in progress;
8. clear completed task entries and synchronize `PROJECT_STATE.md` at closure.

## Guardrail
Do not invent a new feature wave or STEP number from stale documents. New user-visible capabilities require explicit approval and version planning; regressions and compatibility fixes may proceed on the `0.1.x` maintenance line.
