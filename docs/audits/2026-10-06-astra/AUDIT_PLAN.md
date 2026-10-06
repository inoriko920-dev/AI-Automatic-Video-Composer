# ASTRA Bug Audit Plan — AAVC — 2026-10-06

Canonical source supplied by user: `00_ASTRA_BUG_AUDIT_PLAN_AAVC_2026-10-06.docx`
SHA-256: `7e8bace848baf649660ac64022d1786eccc2193b458897aea23b0d17184c478f`
Baseline audited: `main @ 8feeeb2e6e90489e5edb890ee67f3f59ca3d438c`.

This file is the repository-searchable SOL mirror of the user-supplied ASTRA report. It preserves the implementation decisions and acceptance gates needed for maintenance work. The binary DOCX itself was not uploaded by the available GitHub connector.

## Scope
Maintenance only. Do not reopen Software Factory STEP 00–15, redesign UI, change providers, alter frozen release tags, or expand product scope.

## Findings

### AAVC-ASTRA-01 — P1 — Invalid project accepted before active session replacement
Owners: `src/aavc/persistence/serializer.py`, `src/aavc/application/services/project_session.py`, `src/aavc/persistence/recovery.py`, open-project UI boundary.

Required fix:
- validate canonical project structure before session/recovery mutation;
- reject invalid root/nested types, unsupported future schema, invalid scene asset counts, duplicate scene numbers, non-finite/negative numeric values, inconsistent bindings/quotes;
- keep missing media loadable for relink;
- use one canonical validator for load/recovery;
- preserve transactionality: failed open/restore must not change current project/path/history/saved baseline or main/backup bytes.

Acceptance:
- root array/null/scalar and malformed nested payloads fail as controlled persistence/domain errors;
- 0/3-asset scenes, duplicates, NaN/Infinity/negative durations fail;
- schema 1 valid migration still works;
- missing media still opens;
- valid save/load unchanged.

### AAVC-ASTRA-02 — P1 — Large FFmpeg command exceeds Windows CreateProcess command-line limit
Owner: `src/aavc/rendering/ffmpeg_builder.py` plus render executor/process runner.

Required fix:
- separate filter-graph construction from transport;
- serialize final canonical graph to a unique temporary graph/script file after all full/selection mutations;
- keep ProcessRunner canonical and never use `shell=True`;
- cleanup graph temp on success/failure;
- preflight final Windows command length after quoting and fail clearly if non-graph arguments alone remain impossible.

Acceptance:
- 100-scene Rise/Drift fixture no longer requires oversized command line;
- full and selection render use equivalent graph semantics;
- paths with spaces/Unicode/long names covered;
- temp graph cleaned and existing output preserved on render failure;
- native Windows render remains required for final gate.

### AAVC-ASTRA-03 — P2 — Subtitle export fails when ASS path contains apostrophe
Owner: canonical FFmpeg builder and export services.

Required fix:
- correct FFmpeg filter-value escaping, not shell quoting;
- cover apostrophe, spaces, Unicode, comma, semicolon, brackets and Windows drive-letter/backslash forms;
- retain unique ASS staging and cleanup;
- verify full and selection export.

Acceptance:
- real FFmpeg integration succeeds for normal/space/apostrophe/Unicode paths;
- original SRT unchanged and ASS staging removed;
- intentional failure preserves prior output bytes.

### AAVC-ASTRA-04 — P2 — Preview clock drifts when rendering callbacks are late
Owner: `src/aavc/presentation/native_motion_playback.py` and timeline/selection call-sites.

Required fix:
- monotonic elapsed playback clock is canonical; timer only triggers redraw;
- map global elapsed time to scene/local time, preserving residual time across scene boundaries;
- skip stale visual frames when needed;
- preserve anchors for seek, pause/resume, selection, loop, frame step and project change;
- when narration is active, use a consistent audio-clock rule with fallback.

Acceptance:
- fake clock +1s advances timeline ~1s regardless of callback count;
- residual time across multiple scenes maps correctly;
- manual Windows audio drift target <=100 ms after settling;
- no orphan timers/players after replacement.

### AAVC-ASTRA-05 — P2 — Pause resets playhead to start of scene
Owner: `src/aavc/presentation/native_motion_playback.py` plus selection/keyboard-seek call-sites.

Required fix:
- separate Pause semantics from Stop/reset;
- Pause retains frame/local/global position/slider/clock anchor and pauses audio;
- Resume continues from the same position;
- Stop/reset behavior remains for intents that require reset.

Acceptance:
- pause retains timecode/slider within one frame;
- waiting while paused does not advance;
- resume continues from paused position;
- scrub/navigation/selection/loop remain consistent without duplicate timers.

## Required implementation order
0. Repository docs/baseline.
1. ASTRA-01.
2. ASTRA-02 + ASTRA-03.
3. ASTRA-04 + ASTRA-05.
4. Full integration, CI/CodeQL, Windows packaging and target-runtime verification.

## Invariants
- architecture remains presentation -> application -> domain; infrastructure/adapters outside;
- ProjectSession, ProcessRunner, temp uniqueness, atomic output and ASS cleanup remain canonical;
- no real API keys in tests/evidence;
- published `v0.1.1` is untouched;
- no claim of final stability until Windows-specific gates pass.

## Canonical gates
```
python scripts/check_no_secrets.py
python -m compileall -q src
python -m ruff check src tests
python -m mypy src/aavc
python -m pytest -m "not integration and not visual and not e2e" -q
python scripts/capture_step09_ui.py
```

Final closure must synchronize `docs/TASKS.md` and `docs/PROJECT_STATE.md` with fresh evidence.
