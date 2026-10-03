# AI Automatic Video Composer

Windows desktop application for composing narrative/infographic videos from scene DOCX + canonical `Axxx.png` assets.

## Current project state

Development is currently through **STEP 11 — Feature Implementation Waves** on the technical track.

- STEP 00–08: complete
- STEP 09: UI shell implemented, formal parity gate still waiting for actual Windows/PySide6 screenshots
- STEP 10: technical vertical slice complete
- STEP 11: technical feature waves complete

## Technology baseline

- Python 3.12 x64
- PySide6 / Qt Widgets
- Modular monolith
- `presentation -> application -> domain`
- FFmpeg / ffprobe media pipeline
- ASS/libass subtitle pipeline
- PyInstaller onedir portable packaging

## Implemented technical capabilities

- Prompt-1 DOCX scene parsing and canonical `Axxx` asset binding
- SINGLE / DOUBLE layout contracts
- versioned `.aavcproj` ProjectState persistence
- undo / redo and recovery snapshots
- 21-effect visual animation registry
- deterministic random animation with seed, cooldown and lock awareness
- subtitle styling and subtitle animation compilation to ASS
- word-timing fallback
- 1080p FFmpeg render vertical slice
- Documentary Crisp render-quality profile
- validation and relink foundations
- Windows CI / packaging workflow definitions

## Frozen UI reference pack

The repository includes 47 frozen UI references under `resources/ui_reference/final/`. They are visual references, not static screens. Real Qt widgets must follow the normalized UI Freeze rules rather than copying accidental overlaps from generated references.

## Canonical local commands (PowerShell)

```powershell
./scripts/dev.ps1
./scripts/test.ps1
./scripts/package.ps1
./scripts/verify_portable.ps1
```

## Important formal gate

Before STEP 09 is formally closed, actual Windows/PySide6 screenshots still need to be captured and reviewed against the frozen UI references. Technical work after STEP 09 exists, but formal gate status must remain visible until that evidence is accepted.

See `STEP09_STATUS.md`, `STEP10_STATUS.md`, `STEP11_STATUS.md`, and `docs/` for the current architecture and planning contracts.
