# STEP 13 — SECURITY & PRIVACY CHECK

## PASS controls
- Raw provider keys are stored behind `CredentialStore`; production target is Windows Credential Manager.
- ProjectState/key-pool snapshots contain opaque references, not raw API keys.
- Gemini sends the key in `x-goog-api-key`, not in a URL.
- Diagnostic redaction covers API-key/authorization/bearer/token/secret/password assignments, bearer values, Google-style API keys, mappings, and sequences.
- Support bundles redact metadata and included text/log files before ZIP creation.
- CI and unit tests use synthetic credentials and fake/injected provider transports.
- Provider credential backup is not used to evade quota/rate limits: quota/rate/transient failures are surfaced and block automatic credential hopping.
- Authentication or missing-credential failure may disable an unusable credential and select an explicitly configured backup.

## Privacy boundaries
- No telemetry/upload service is introduced by STEP 13.
- No conversation or project data is sent to an AI provider unless a provider call is explicitly initiated by application workflow.
- Provider context builder remains responsible for minimizing/truncating outbound context.

## Provisional / release checks
- Manual live-provider test is optional and must never expose a real key in logs/screenshots.
- Exact packaged RC must be scanned for accidentally embedded credentials, local absolute paths, test secrets, and debug artifacts.
- Third-party binary/license notices, especially the final FFmpeg build, must be verified in STEP 14.
