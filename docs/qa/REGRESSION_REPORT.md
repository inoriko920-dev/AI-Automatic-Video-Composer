# STEP 13 — REGRESSION REPORT

## Protected baselines
STEP 13 must preserve the closed gates from STEP 09–12:
- STEP 09 real Qt shell and representative screenshots.
- STEP 10 DOCX → asset binding → ProjectState → layout → subtitle → FFmpeg vertical slice.
- STEP 11 undo/redo, relink/validation, animation registry/random behavior, subtitle styling/animation, render-quality preset, recovery.
- STEP 12 provider boundary, Gemini adapter, credential storage, context minimization/redaction.

## Latest established regression evidence before close
Windows CI run #103 (`69c19b3e95bbc2db48c5ee3f4a69bc00dfe63ce5`) passed Compile, Ruff, strict mypy, 51 cheap tests, 8 Qt captures, screenshot verification, and artifact upload.

## STEP 13 delta requiring final rerun
Credential handling was hardened after run #103 so that rate-limit/quota/transient failures cannot hop to another credential automatically. Tests now verify:
- quota failure is surfaced;
- only the active credential is attempted;
- active credential enters cooldown;
- configured backup remains unused for quota;
- authentication failure may disable an invalid credential and select a backup.

## Regression decision
No prior gate is intentionally weakened. Final STEP 13 closure requires one green Windows CI run from the exact closing SHA.
