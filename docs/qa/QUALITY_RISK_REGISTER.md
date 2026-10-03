# STEP 13 — QUALITY RISK REGISTER

| ID | Risk | Severity | Mitigation / Evidence | State |
|---|---|---:|---|---|
| QR-01 | Secret/API key leaks into logs, snapshots, support bundles | Critical | recursive redaction, Google-key/Bearer patterns, credential references only, diagnostics tests | Mitigated |
| QR-02 | Multiple credentials used to bypass quota/rate limits | High | sticky active credential; quota/rate/transient surfaced; backup only after auth/missing credential | Mitigated |
| QR-03 | Background task freezes UI or cannot be cancelled | High | ThreadPool JobManager + CancellationToken + deterministic job-state tests | Mitigated |
| QR-04 | Child process hangs indefinitely | High | ProcessRunner timeout normalization and launch-error boundary | Mitigated |
| QR-05 | Render starts with missing/invalid required inputs | High | preflight validation + output validation + failure-path tests | Mitigated |
| QR-06 | STEP 13 changes regress UI shell | High | Windows CI recaptures/verifies 8 real Qt reference states on every gate run | Mitigated |
| QR-07 | Portable build works only in dev environment | High | STEP 14 must build/extract/smoke exact RC ZIP on Windows | Open for STEP 14 |
| QR-08 | Bundled FFmpeg provenance/license/capability mismatch | High | keep binary bundling gated; exact release candidate must record provenance/license/capability | Open for STEP 14 |
| QR-09 | DPI 125%/150% exposes layout clipping not seen at 100% | Medium | current 1920×1080 representative gate passes; dedicated DPI matrix remains | Provisional |
| QR-10 | Live Gemini behavior differs from injected fake transport | Medium | provider boundary deterministic; live network test intentionally excluded from CI | Provisional |
| QR-11 | Very large real projects expose memory/performance issues | Medium | deterministic component tests exist; large-project benchmark deferred | Provisional |

STEP 14 may not downgrade an Open/Provisional risk to PASS without corresponding evidence.
