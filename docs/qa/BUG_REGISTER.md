# STEP 13 — BUG REGISTER

| ID | Finding | Severity | Resolution | Status |
|---|---|---:|---|---|
| BUG-13-001 | Provider quota/rate failure could automatically continue on another configured credential | High | sticky active credential + no automatic failover for quota/rate/transient + regression tests | Fixed; final CI required |
| BUG-13-002 | Child-process timeout/launch errors needed stable application-level error types | High | `ProcessTimeoutError` and `ProcessLaunchError` normalization | Fixed |
| BUG-13-003 | Diagnostic/support evidence could contain secrets if arbitrary text was copied verbatim | Critical | recursive structured redaction + redacted bundle writer | Fixed |
| BUG-13-004 | Background work had no concrete cancellable job lifecycle | High | `CancellationToken`, `BackgroundJob`, `JobManager` | Fixed |
| BUG-13-005 | Render preflight/output validation was too thin for professional QA | High | preflight/output validators + failure-path tests | Fixed |

## Open release-level findings
No code defect from this register is intentionally carried into STEP 14. The following are evidence gaps rather than confirmed defects: clean-machine packaged smoke, exact RC checksum/manifest/provenance, DPI 125%/150%, large-project performance, and approved FFmpeg bundle provenance.
