# STEP 15 — Final Release / Backup / Maintenance

Status: **IN PROGRESS**

Implemented:
- final version bumped to `0.1.0`
- final release notes, maintenance policy, backup/recovery policy
- explicit FFmpeg/ffprobe distribution decision: not redistributed in 0.1.0; resolved from app-local `tools/ffmpeg/` or Windows PATH
- runtime media-tool resolver with deterministic tests
- final PyInstaller portable content contract
- final Windows workflow producing portable ZIP, source-backup ZIP, BUILD_INFO and SHA256SUMS

Gate remains open until the final Windows workflow passes compile, Ruff, strict mypy, cheap pytest, representative Qt screenshots, portable smoke, archive generation and artifact upload on `bootstrap/step15`.
