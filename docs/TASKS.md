# ACTIVE TASKS — Post Release 0.1.1

## Current queue
**#260 — 0.2 completion wave: ACTIVE**

Software Factory STEP 00–15 remains complete and published `v0.1.1` stays frozen. The approved 0.2 source completion wave is being finished separately on `main`.

### 0.2 completion wave — #260
Status: **ACTIVE**

Completed runtime work:
- project/File/Export action-state synchronization (#258/#259);
- real microphone narration workflow (#261/#262);
- bounded live Gemini Auto (AI) using secure credential slots (#263/#264);
- responsive background render/Gemini work through canonical JobManager (#265/#266);
- visible-placeholder cleanup and documentation synchronization (#267).

Next exact action after #267 merges:
- run compile, Ruff, strict mypy, pytest, STEP09 screenshot verification, and CodeQL on merged `main`;
- produce a fresh Windows portable **test build** from the completed source line;
- verify that build before closing #260.


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
