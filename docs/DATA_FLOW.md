# DATA_FLOW

## Manual edit
Widget action → application command → validate → ProjectSession transaction → ProjectState new revision → state event → UI refresh → autosave schedule.

## Random animation
UI scope/seed → RandomizeAnimationCommand → lock checks → AnimationPlanner → one compound state patch → preview refresh; renderer never randomizes.

## AI edit
Instruction → ContextBuilder → Provider job → validated ActionPlan → UI review → ApplyAIPlanCommand → one compound undo checkpoint → state event.

## Import
Wizard → ImportProjectCommand → worker probes DOCX/assets/media → normalized ImportResult → UI review/errors → CommitImportCommand.

## Preview
ProjectSnapshot → RenderPlan/PreviewPlan → cached base proxy + PlaybackClock → Qt overlay evaluator → monitor.

## Render
Export preflight → RenderJob → compile RenderPlan → FFmpeg process → progress parser → ffprobe validate → atomic finalize → success event.
