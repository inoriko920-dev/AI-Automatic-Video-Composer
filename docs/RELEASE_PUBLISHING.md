# GitHub Release Publishing — AAVC 0.1.x

## Current publication status

**0.1.1 — PUBLISHED / VERIFIED**

Official GitHub Release `v0.1.1` was published on 2026-10-04 as a maintenance patch.

Canonical evidence:
- Version: `0.1.1`
- Git tag: `v0.1.1`
- Frozen source ref: `release/0.1.1`
- Sealed source commit: `a6515ee7c4c9cda88a0c8aa93892c36eaf292d2e`
- Maintenance Release Windows 0.1.1 run: `#1` / `37181599863`
- Windows ZIP SHA-256: `84ad8cc93f055cb95fc2624511a9eecd541505627628090c277a048e5e8495b4`
- Source ZIP SHA-256: `a5a00b196e76d34684deef97b9dc605b748e1a32f2f92fe6f761c25b13f720bb`

`BUILD_INFO.txt` records the same release commit and version `0.1.1`. `SHA256SUMS.txt` matches independently computed hashes for both release ZIP files.

Direct artifact inspection confirmed that the Windows ZIP contains `AI Automatic Video Composer.exe` and `tools/ffmpeg/README.md` at portable root, with no redundant `_internal/tools/ffmpeg/README.md` copy.

## 0.1.1 published files

- `AI-Automatic-Video-Composer-0.1.1-win64.zip`
- `AI-Automatic-Video-Composer-0.1.1-source.zip`
- `RELEASE_NOTES_0.1.1.md`
- `MAINTENANCE.md`
- `BACKUP_AND_RECOVERY.md`
- `BUILD_INFO.txt`
- `SHA256SUMS.txt`

## 0.1.1 guarded publication design

The maintenance workflow builds only from frozen `release/0.1.1`, validates version `0.1.1`, runs all release gates, and refuses to overwrite an existing `v0.1.1` tag or GitHub Release. The workflow stored on `main` is manual-only; there is no persistent push-to-publish trigger.

A one-shot branch was used to bridge the chat connector's lack of `workflow_dispatch`. The first run published `v0.1.1` successfully. A second duplicate attempt reached the overwrite guard and was rejected, proving that the existing release/tag was not replaced. The one-shot branch was then retired and its marker removed.

Do **not** repeat publication for `v0.1.1`; the existing immutable release is the canonical artifact.

## Historical 0.1.0 release

Official GitHub Release `v0.1.0` remains published and unchanged.

Canonical evidence:
- Frozen source ref: `release/0.1.0`
- Sealed source commit: `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Final Release Windows run: `#6` / `37180132492`
- Windows ZIP SHA-256: `c3e4f92656aefd3d57329627c52b8e057d2f8cac5a0a757471b90cb1d68915e8`
- Source ZIP SHA-256: `1264b1dc483932b496acf87dee21c93f92d4e1b222aa37ca2284fbf99b9df328`

## Historical workflow retirement

The original `release-candidate.yml` and `release-final.yml` workflows are retained only for reproducibility and historical verification. Both are now `workflow_dispatch`-only and use read-only repository permissions.

- RC verification is pinned to `release/step14-rc1` and cannot run automatically from the old `bootstrap/step14` branch.
- Final 0.1.0 verification is pinned to `release/0.1.0` and no longer contains a GitHub Release publication job or any `contents: write` permission.
- Their uploaded artifacts are explicitly named as historical verification artifacts so they cannot be confused with canonical published releases.

These historical workflows must not be used to publish a new release. New maintenance versions must use a newly planned, version-specific frozen source and guarded publication workflow.

## Future releases

Do not move or replace published `v0.1.0` or `v0.1.1` tags in place. Corrections must use an explicitly planned new version under `MAINTENANCE.md`.

For a later patch/minor/major release, define the new version, frozen source, release notes, compatibility implications, release gates, and guarded publication path before publication.
