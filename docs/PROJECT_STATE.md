# PROJECT_STATE — Post STEP 15 / Release 0.1.0

- Factory Steps: 00–15 complete
- Status: PASS
- Current release: `0.1.0`
- GitHub Release publication: **PENDING MANUAL DISPATCH**
- Frozen release source: `release/0.1.0` @ `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`
- Maintenance line: `0.1.x`
- Architecture: ARCH-AAVC-v1.0
- Product Blueprint: PB-AAVC-v1.0
- UI Freeze: UIF-AAVC-v1.0
- Code Constitution: CC-AAVC-v1.0
- Repository: `inoriko920-dev/AI-Automatic-Video-Composer`
- Primary branch: `main`

## IMPLEMENTED
Production source, UI, end-to-end composition flow, external/provider integration, hardening/QA, Windows portable packaging, release-candidate gate, final-release gate, backup/recovery policy, maintenance policy, and guarded GitHub Release publishing workflow are implemented through STEP 15 and post-release maintenance.

See `README.md`, `STEP15_STATUS.md`, `FINAL_RELEASE_MANIFEST.md`, and `docs/RELEASE_PUBLISHING.md` for the canonical capability, release, and publishing summary.

## VERIFIED
The final 0.1.0 release gate passed on Windows. Required quality gates include compileall, Ruff, strict mypy, pytest, representative STEP 09 Qt screenshot verification, portable PyInstaller smoke verification, release-content validation, secret exclusion, and SHA-256 generation.

Post-release CI on `main` also passes after the guarded publishing fixes and release-publishing documentation were merged.

Canonical release evidence is recorded in `STEP15_STATUS.md` and `FINAL_RELEASE_MANIFEST.md`.

## PROVISIONAL / EXTERNAL WATCH
No factory blocker remains. Before patch releases, re-check compatibility when Gemini/provider behavior, PySide6/Qt, Python 3.12 support, FFmpeg capability/license profile, or Windows 11 packaging/runtime behavior changes.

## BLOCKERS
No code, CI, or packaging blocker is currently known. Official GitHub Release publication still requires a manual `workflow_dispatch` because repository tooling in this workflow intentionally requires explicit operator opt-in before publishing a permanent release/tag.

## ACTIVE TASK
`REL-0.1.0-PUBLISH` — publish official GitHub Release `v0.1.0` from frozen source `release/0.1.0`.

No product feature wave is active.

## NEXT EXACT ACTION
Run `Final Release Windows` manually with:
- `publish_github_release = true`
- `release_tag = v0.1.0`
- `release_source_ref = release/0.1.0`

After the run succeeds, verify that tag `v0.1.0` resolves to commit `92da28bbb8177b11b3d09f000a4e7e01d389ccc5`, required release assets are present, and published SHA-256 values match the generated checksum file. Then mark `REL-0.1.0-PUBLISH` complete.

For any later requested product change, classify it under `MAINTENANCE.md` before implementation. Do not restart completed STEP 09–15 work unless regression evidence requires it.
