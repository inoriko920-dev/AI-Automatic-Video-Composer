# ACTIVE FACTORY TASKS

## STEP 13 — Hardening & QA
- S13-T01 — Secret redaction + structured diagnostics: DONE.
- S13-T02 — Redacted support bundle: DONE.
- S13-T03 — Cancellable background-job lifecycle: DONE.
- S13-T04 — Process timeout/launch error normalization: DONE.
- S13-T05 — Render preflight/output validation: DONE.
- S13-T06 — Provider credential policy: quota/rate/transient must not auto-hop credentials: DONE.
- S13-T07 — Canonical QA evidence pack: DONE.
- S13-T08 — Final Windows CI on closing SHA: PENDING.

## STEP 14 — Release Candidate & Packaging (next after S13-T08 PASS)
1. S14-T01 — Branch `release/step14-rc1` from exact STEP 13 closing SHA and freeze RC identity.
2. S14-T02 — Upgrade Windows package workflow to exact RC artifact naming/version/SHA.
3. S14-T03 — Build manifest + SHA-256 checksum + build provenance.
4. S14-T04 — Extract candidate ZIP to a fresh folder and smoke the packaged app.
5. S14-T05 — Run candidate hygiene/security scan and record evidence.
6. S14-T06 — RC gate decision and handoff to STEP 15.

No new product feature may enter STEP 14 without an explicit blocker fix and complete regression run.
