# STEP 13 — TEST MATRIX

| Area | Test / Gate | Level | Windows CI |
|---|---|---|---|
| Syntax/import | `python -m compileall -q src` | Build | Required |
| Style/static | Ruff `src tests` | Static | Required |
| Types | strict mypy `src/aavc` | Static | Required |
| Project/import/layout/subtitle/animation | STEP 10–11 tests | Unit/contract | Required |
| Provider context/credential/Gemini/manager | STEP 12 tests | Unit | Required |
| Redaction + support bundle | `test_step13_diagnostics.py` | Security unit | Required |
| Job cancel/state/failure | `test_step13_jobs.py` | Concurrency unit | Required |
| Process timeout/launch normalization | `test_step13_process_runner.py` | Platform unit | Required |
| Render preflight/output validation | `test_step13_render_hardening.py` | Render unit | Required |
| Real Qt representative UI | capture UI-002/003/010/013/014/027/035/041 | UI regression | Required |
| Screenshot existence/size | 8 PNG verification | UI gate | Required |
| UI evidence artifact | `step09-ui-actual` upload | Evidence | Required |
| FFmpeg integration render | STEP 10 integration test | Integration | Available; not in cheap-test gate |
| Portable exact RC after extraction | STEP 14 | Packaging/e2e | Pending STEP 14 |
| DPI 125% / 150% | STEP 14/15 candidate QA | UI system | Provisional |
| Live Gemini account/network | Manual optional diagnostic only | External | Not required / no CI secret |

## Gate principle
A feature is not considered release-ready merely because a unit test passes. STEP 14 must validate the exact packaged candidate produced from a frozen SHA.
