# GitHub Release Publishing — AAVC 0.1.0

This document describes the guarded publication path for the already-sealed `0.1.0` release.

## Canonical release source

- Version: `0.1.0`
- Git tag to create: `v0.1.0`
- Frozen source ref: `release/0.1.0`
- Expected sealed source commit: `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Workflow: `Final Release Windows`

The official `v0.1.0` release must be built from the frozen `release/0.1.0` ref. Do not publish `v0.1.0` from `main`, because `main` contains post-release documentation and CI maintenance commits.

## Publish from GitHub Actions

1. Open **Actions** -> **Final Release Windows**.
2. Choose **Run workflow** from the default branch containing the current workflow definition.
3. Set `publish_github_release` to `true`.
4. Keep `release_tag` as `v0.1.0`.
5. Keep `release_source_ref` as `release/0.1.0`.
6. Run the workflow.

The workflow then:

1. checks out the frozen release source;
2. records the exact source commit;
3. runs compileall, Ruff, strict mypy, cheap pytest, STEP 09 screenshot capture/verification, PyInstaller packaging and portable verification;
4. creates the final portable ZIP and exact source ZIP;
5. writes `BUILD_INFO.txt` and `SHA256SUMS.txt`;
6. uploads the verified bundle as an Actions artifact;
7. only after all gates pass, creates the GitHub Release and `v0.1.0` tag targeting the resolved frozen source commit.

## Expected published files

- `AI-Automatic-Video-Composer-0.1.0-win64.zip`
- `AI-Automatic-Video-Composer-0.1.0-source.zip`
- `RELEASE_NOTES_0.1.0.md`
- `MAINTENANCE.md`
- `BACKUP_AND_RECOVERY.md`
- `BUILD_INFO.txt`
- `SHA256SUMS.txt`

## Safety rules

- The workflow refuses to overwrite an existing GitHub Release.
- The workflow refuses to overwrite an existing tag.
- The official 0.1.0 publish path rejects a tag other than `v0.1.0`.
- The official 0.1.0 publish path rejects a source ref other than `release/0.1.0`.
- Do not move the frozen release branch after publication.
- Do not commit API keys or user runtime data into release assets.

## Verification after publication

Confirm that:

1. GitHub Releases contains `v0.1.0`;
2. the tag resolves to commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`;
3. all expected files are attached;
4. the portable and source ZIP hashes match `SHA256SUMS.txt`;
5. `BUILD_INFO.txt` records the same release commit and version `0.1.0`.

If any of these checks fail, treat the publication as invalid and do not replace the existing tag in place. Investigate and use an explicitly planned corrective release instead.
