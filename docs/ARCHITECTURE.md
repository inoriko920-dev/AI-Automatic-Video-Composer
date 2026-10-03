# ARCHITECTURE — AI Automatic Video Composer

Architecture ID: **ARCH-AAVC-v1.0**  
Status: **PASS_WITH_PROVISIONAL**  
Blueprint: PB-AAVC-v1.0 / UIF-AAVC-v1.0

## Chosen Architecture
Modular monolith Windows desktop app. Presentation (PySide6 Qt Widgets) -> Application commands/use-cases -> Domain. Infrastructure implements ports for filesystem, persistence, FFmpeg/ffprobe, HTTP providers, credentials, logging, jobs and paths.

## Chosen Stack
- Python 3.12 x64; exact patch pinned at repository foundation.
- PySide6 Qt Widgets.
- Bundled ffmpeg/ffprobe CLI through centralized ToolRegistry/ProcessRunner.
- Versioned JSON `.aavcproj`, atomic save + separate recovery snapshots.
- RationalTime `{num, den}` canonical time model.
- Windows Credential Manager for raw API keys.
- PyInstaller `onedir` portable folder, then ZIP + checksums.
- GitHub Actions Windows build/test/package.

## Non-negotiable Dependency Direction
`presentation -> application -> domain`

Infrastructure implements ports; domain never imports Qt, HTTP, filesystem details, provider SDK, or FFmpeg. No raw subprocess outside ProcessRunner. No raw provider transport outside providers.

## Media Strategy
A backend-neutral immutable RenderPlan is compiled from ProjectState. Preview uses a cached low-resolution base proxy plus Qt live overlays. Final render uses FFmpeg graph + ASS/libass subtitle compilation. Same AnimationSpec, RationalTime and seed feed both.

## Provisional Validation
1. Exact FFmpeg binary/config/license/capability profile.
2. Preview-vs-final parity for SINGLE, DOUBLE, complex reveal and karaoke.
3. Exact pinned patch versions and preview proxy codec.

None blocks STEP 07.
