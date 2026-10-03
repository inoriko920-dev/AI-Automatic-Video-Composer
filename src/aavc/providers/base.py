from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class ProviderFailureKind(StrEnum):
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"
    QUOTA = "quota"
    TRANSIENT = "transient"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    prompt: str
    model: str
    system_instruction: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    text: str
    provider: str
    model: str
    key_ref: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ProviderCallError(RuntimeError):
    def __init__(
        self,
        kind: ProviderFailureKind,
        message: str,
        *,
        retryable: bool,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.retryable = retryable
        self.status_code = status_code


class ProviderAdapter(Protocol):
    name: str

    def generate(self, request: ProviderRequest, *, api_key: str) -> ProviderResponse:
        """Generate text using the supplied secret without retaining it."""
