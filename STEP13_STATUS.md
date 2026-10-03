# STEP 13 — Hardening & QA

Status: **IN PROGRESS**

Implemented in this wave:
- render-plan preflight validation for dimensions, FPS, scene duration, missing media, narration, subtitle and output path warnings
- cooperative background `JobManager` with terminal COMPLETED / FAILED / CANCELLED states
- diagnostics redaction for explicit secrets, Gemini-shaped API keys, Bearer tokens and common secret assignments
- redacted diagnostics ZIP writer
- deterministic STEP 13 negative-path/unit tests

Gate is not PASS until Windows CI completes compile, Ruff, strict mypy, cheap pytest, and representative Qt screenshot capture successfully on this branch.
