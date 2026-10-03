# STEP 13 — Hardening & QA

Status: **IN PROGRESS**

Hardening targets:
- sensitive-data redaction and structured diagnostics
- support bundle generation without secrets
- cancellable background-job primitives
- render preflight and output validation
- subprocess timeout normalization
- deterministic unit/contract tests for failure paths
- regression protection for STEP 09–12 behavior

Exit gate:
Compile, Ruff, strict mypy, pytest, Qt screenshot regression capture/verification, and diagnostics/security tests must all pass on Windows CI.
