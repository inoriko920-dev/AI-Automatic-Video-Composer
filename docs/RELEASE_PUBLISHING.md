# GitHub Release Publishing — AAVC 0.1.0

## Publication status

**PUBLISHED / VERIFIED**

Official GitHub Release `v0.1.0` was published on 2026-10-04.

Canonical evidence:
- Version: `0.1.0`
- Git tag: `v0.1.0`
- Frozen source ref: `release/0.1.0`
- Sealed source commit: `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Final Release Windows run: `#6` / `37180132492`
- Windows ZIP SHA-256: `c3e4f92656aefd3d57329627c52b8e057d2f8cac5a0a757471b90cb1d68915e8`
- Source ZIP SHA-256: `1264b1dc483932b496acf87dee21c93f92d4e1b222aa37ca2284fbf99b9df328`

`BUILD_INFO.txt` records the same release commit and version `0.1.0`. `SHA256SUMS.txt` matches independently computed hashes for both release ZIP files.

## Published files

- `AI-Automatic-Video-Composer-0.1.0-win64.zip`
- `AI-Automatic-Video-Composer-0.1.0-source.zip`
- `RELEASE_NOTES_0.1.0.md`
- `MAINTENANCE.md`
- `BACKUP_AND_RECOVERY.md`
- `BUILD_INFO.txt`
- `SHA256SUMS.txt`

## Guarded publication design

The canonical release workflow remains guarded:

1. official `v0.1.0` publication is sealed to `release/0.1.0`;
2. release/tag overwrite is refused;
3. publication requires the final-release gate to pass first;
4. only the publish job receives `contents: write`;
5. normal CI and build jobs remain read-only.

A temporary one-shot push trigger was used only to bridge the chat connector's lack of `workflow_dispatch`. After successful publication it was retired and the canonical workflow returned to manual `workflow_dispatch` behavior.

## Historical operator procedure

Before `v0.1.0` existed, the intended manual procedure was:

1. Open **Actions** -> **Final Release Windows**.
2. Choose **Run workflow** from the default branch containing the current workflow definition.
3. Set `publish_github_release` to `true`.
4. Keep `release_tag` as `v0.1.0`.
5. Keep `release_source_ref` as `release/0.1.0`.
6. Run the workflow.

Do **not** repeat that publication now. The workflow is intentionally expected to refuse overwrite because `v0.1.0` already exists.

## Future releases

Do not move or replace the published `v0.1.0` tag in place. Corrections must use an explicitly planned new version under `MAINTENANCE.md`.

For a later patch/minor/major release, define the new version, release source, release notes, migration/compatibility implications, and release workflow inputs before publication.
