from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

_SECRET_KEY_PATTERN = re.compile(
    r"(?i)(api[_ -]?key|authorization|bearer|token|secret|password)\s*[:=]\s*([^\s,;]+)"
)


class ProviderContextBuilder:
    def __init__(self, *, max_chars: int = 24_000) -> None:
        if max_chars < 256:
            raise ValueError("max_chars must be at least 256")
        self._max_chars = max_chars

    def build(
        self,
        instruction: str,
        *,
        scene_id: str | None = None,
        asset_ids: Sequence[str] = (),
        metadata: Mapping[str, str] | None = None,
        notes: Sequence[str] = (),
    ) -> str:
        sections: list[str] = [f"INSTRUCTION\n{redact_secrets(instruction.strip())}"]
        if scene_id:
            sections.append(f"SCENE\n{redact_secrets(scene_id.strip())}")
        if asset_ids:
            safe_assets = ", ".join(redact_secrets(value.strip()) for value in asset_ids)
            sections.append(f"ASSETS\n{safe_assets}")
        if metadata:
            safe_lines: list[str] = []
            for key in sorted(metadata):
                if _looks_sensitive_key(key):
                    continue
                value = redact_secrets(metadata[key].strip())
                safe_lines.append(f"{key}: {value}")
            if safe_lines:
                sections.append("METADATA\n" + "\n".join(safe_lines))
        if notes:
            safe_notes = [redact_secrets(note.strip()) for note in notes if note.strip()]
            if safe_notes:
                sections.append("NOTES\n" + "\n".join(f"- {note}" for note in safe_notes))

        combined = "\n\n".join(section for section in sections if section.strip())
        if len(combined) <= self._max_chars:
            return combined
        marker = "\n\n[CONTEXT_TRUNCATED]"
        keep = max(0, self._max_chars - len(marker))
        return combined[:keep].rstrip() + marker


def redact_secrets(text: str) -> str:
    return _SECRET_KEY_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)


def _looks_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return any(
        token in normalized
        for token in ("apikey", "authorization", "bearer", "token", "secret", "password")
    )
