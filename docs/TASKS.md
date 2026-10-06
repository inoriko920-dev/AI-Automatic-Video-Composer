# ACTIVE TASKS — Post Release 0.1.1

## Current queue
No technical implementation task is active. Completion wave #260 and final technical cleanup #274 are complete. Remaining open repository items #20 (branch protection) and #27 (project license) require owner/admin decisions.

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

Final verified 0.2 build evidence:
- application source `2efd414b6a582b86d39c5b6d1f7d4ff7d0bb6897`;
- CI run `37420784262`: PASS;
- CodeQL run `37420784256`: PASS;
- packaging run `37420955954`: PASS;
- Actions artifact ID `11392374584`;
- artifact wrapper SHA-256 `0fc80d64e1a022dd2c4530c89186316217ae1ad0d062eb1bbd39520139a1e221`;
- portable ZIP SHA-256 `a59737cd2cf5766eb3c2b7c76d2c549dbbb435f1db7ad84683efd3d7489d7802`.

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

Next action is direct user testing. New capability work still requires explicit approval.


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
