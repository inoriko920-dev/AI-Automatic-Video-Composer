# ACTIVE TASKS — Post Release 0.1.0

## Current queue
No product feature task is active.

Software Factory STEP 00–15 is complete. The old STEP 09 ready-task list is retired and must not be treated as pending work.

### REL-0.1.0-PUBLISH — Publish official GitHub Release
Status: **COMPLETE**

Official GitHub Release `v0.1.0` was published successfully on 2026-10-04 from frozen source `release/0.1.0`, commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.

Verified evidence:
- Final Release Windows run: `#6` / `37180132492`
- Tag: `v0.1.0`
- Release target commit: `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Windows ZIP SHA-256: `c3e4f92656aefd3d57329627c52b8e057d2f8cac5a0a757471b90cb1d68915e8`
- Source ZIP SHA-256: `1264b1dc483932b496acf87dee21c93f92d4e1b222aa37ca2284fbf99b9df328`
- `BUILD_INFO.txt` records version `0.1.0` and the same frozen release commit.
- `SHA256SUMS.txt` matches independently computed hashes for both release ZIP files.

The temporary one-shot publish trigger used to bridge tooling limitations has been retired. The canonical workflow returns to guarded manual publication behavior and refuses to overwrite an existing tag/release.

## Maintenance intake checklist
When a concrete request arrives:
1. record the symptom or requested capability and expected behavior;
2. search existing implementation/tests before creating modules;
3. classify patch/minor/major impact using `MAINTENANCE.md`;
4. identify affected architecture/UI/schema/provider/packaging contracts;
5. define focused implementation and regression-test tasks;
6. run the required gates and preserve evidence;
7. update this file with the active task IDs while work is in progress;
8. clear completed task entries and synchronize `PROJECT_STATE.md` at closure.

## Guardrail
Do not invent a new feature wave or STEP number from stale documents. New user-visible capabilities require explicit approval and version planning; regressions and compatibility fixes may proceed on the `0.1.x` maintenance line.
