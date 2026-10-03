from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_ -]?key|authorization|bearer|token|secret|password)\b\s*[:=]\s*([^\s,;]+)"
)
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+\-/=]+")
_GOOGLE_KEY = re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")


def redact_text(text: str) -> str:
    value = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    value = _BEARER.sub("Bearer [REDACTED]", value)
    return _GOOGLE_KEY.sub("[REDACTED_API_KEY]", value)


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Mapping):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _looks_sensitive_key(key_text):
                clean[key_text] = "[REDACTED]"
            else:
                clean[key_text] = redact_value(item)
        return clean
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_value(item) for item in value]
    return value


def _looks_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return any(
        token in normalized
        for token in (
            "apikey",
            "authorization",
            "bearer",
            "credential",
            "password",
            "secret",
            "token",
        )
    )
