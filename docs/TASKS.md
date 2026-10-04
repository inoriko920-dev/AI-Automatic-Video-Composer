# ACTIVE TASKS — Maintenance Release 0.1.1

## Current queue
No product feature task is active.

Software Factory STEP 00–15 remains complete. Maintenance work stays on the `0.1.x` line.

### REL-0.1.1-PUBLISH — Publish maintenance patch
Status: **IN PROGRESS**

Scope is limited to maintenance issue #9 and release metadata:
- correct the portable app-local FFmpeg slot to `tools/ffmpeg/` beside the EXE;
- enforce that structure in portable verification;
- remove the redundant `_internal/tools/ffmpeg/README.md` packaging path;
- align package/runtime version metadata to `0.1.1`;
- publish a new immutable `v0.1.1` release without altering `v0.1.0`.

Evidence already passed before release preparation:
- PR #10 CI: PASS;
- independent Windows PyInstaller packaging: PASS;
- portable verifier: PASS;
- direct ZIP inspection confirmed root EXE + `tools/ffmpeg/README.md` and no internal duplicate;
- issue #9 closed after the fix merged to `main`.

Required closure checks:
1. final CI on frozen `release/0.1.1` source passes;
2. maintenance release workflow passes all build/QA gates;
3. GitHub Release `v0.1.1` exists and targets the frozen 0.1.1 source commit;
4. expected Windows/source ZIPs and release documents are attached;
5. published ZIP hashes match `SHA256SUMS.txt`;
6. `BUILD_INFO.txt` records version `0.1.1` and the same frozen commit;
7. release state is synchronized back to `main`.

### REL-0.1.0-PUBLISH — Publish official GitHub Release
Status: **COMPLETE**

Official GitHub Release `v0.1.0` remains the immutable published baseline at commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`.

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
