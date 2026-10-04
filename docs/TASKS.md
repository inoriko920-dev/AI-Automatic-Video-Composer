# ACTIVE TASKS — Post Release 0.1.0

## Current queue
No product feature task is active.

Software Factory STEP 00–15 is complete. The old STEP 09 ready-task list is retired and must not be treated as pending work.

### REL-0.1.0-PUBLISH — Publish official GitHub Release
Status: **PENDING MANUAL DISPATCH**

The final Windows release source is frozen at `release/0.1.0` (commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`). The guarded `Final Release Windows` workflow is ready to rebuild that exact source, run the release gates, and publish tag/release `v0.1.0`.

Required manual workflow inputs:
- `publish_github_release = true`
- `release_tag = v0.1.0`
- `release_source_ref = release/0.1.0`

Do not mark this task complete until the GitHub Release exists, tag `v0.1.0` resolves to the frozen release commit, the published assets are present, and the published checksums are verified.

See `docs/RELEASE_PUBLISHING.md` for the operator procedure.

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
