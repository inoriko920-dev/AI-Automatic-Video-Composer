# STEP 12 — Integration & External Services

Status: **IN PROGRESS**

Scope:
- provider-neutral AI request/response contract
- Gemini REST adapter behind an injectable HTTP transport
- API-key pool with bounded rotation/cooldown/disable behavior
- credential-store boundary with Windows Credential Manager implementation
- context minimization and secret redaction
- deterministic tests that never call a live provider

Security rules:
- raw API keys are not stored in ProjectState or provider pool snapshots
- raw secrets are resolved only immediately before a provider call
- errors/status objects must not echo secrets
- tests use synthetic keys and fake transports only
