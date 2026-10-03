from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from aavc.providers.base import (
    ProviderCallError,
    ProviderFailureKind,
    ProviderRequest,
    ProviderResponse,
)
from aavc.providers.http import JsonHttpTransport, JsonHttpTransportError, UrllibJsonTransport


class GeminiRestAdapter:
    name = "gemini"

    def __init__(
        self,
        transport: JsonHttpTransport | None = None,
        *,
        api_base: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_s: float = 60.0,
    ) -> None:
        self._transport = transport or UrllibJsonTransport()
        self._api_base = api_base.rstrip("/")
        self._timeout_s = timeout_s

    def generate(self, request: ProviderRequest, *, api_key: str) -> ProviderResponse:
        if not api_key:
            raise ProviderCallError(
                ProviderFailureKind.AUTH,
                "Credential is empty",
                retryable=False,
            )
        if not request.prompt.strip():
            raise ProviderCallError(
                ProviderFailureKind.INVALID_REQUEST,
                "Prompt is empty",
                retryable=False,
            )
        if not request.model.strip():
            raise ProviderCallError(
                ProviderFailureKind.INVALID_REQUEST,
                "Model is empty",
                retryable=False,
            )

        model = quote(request.model.strip(), safe="")
        url = f"{self._api_base}/models/{model}:generateContent"
        payload = self._build_payload(request)
        try:
            result = self._transport.post_json(
                url,
                payload,
                headers={"x-goog-api-key": api_key},
                timeout_s=self._timeout_s,
            )
        except JsonHttpTransportError as exc:
            raise self._map_transport_error(exc) from None

        if result.status_code < 200 or result.status_code >= 300:
            raise self._map_status(result.status_code, result.payload)

        text = self._extract_text(result.payload)
        if not text:
            raise ProviderCallError(
                ProviderFailureKind.UNKNOWN,
                "Provider response contained no text candidate",
                retryable=True,
                status_code=result.status_code,
            )
        metadata = self._extract_metadata(result.payload)
        return ProviderResponse(
            text=text,
            provider=self.name,
            model=request.model,
            metadata=metadata,
        )

    @staticmethod
    def _build_payload(request: ProviderRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": request.prompt}]}]
        }
        if request.system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": request.system_instruction}]
            }
        generation_config: dict[str, Any] = {}
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_output_tokens
        if generation_config:
            payload["generationConfig"] = generation_config
        return payload

    @staticmethod
    def _extract_text(payload: Mapping[str, Any]) -> str:
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return ""
        first = candidates[0]
        if not isinstance(first, dict):
            return ""
        content = first.get("content")
        if not isinstance(content, dict):
            return ""
        parts = content.get("parts")
        if not isinstance(parts, list):
            return ""
        chunks: list[str] = []
        for part in parts:
            if isinstance(part, dict):
                value = part.get("text")
                if isinstance(value, str):
                    chunks.append(value)
        return "".join(chunks).strip()

    @staticmethod
    def _extract_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        usage = payload.get("usageMetadata")
        if isinstance(usage, dict):
            for key in (
                "promptTokenCount",
                "candidatesTokenCount",
                "totalTokenCount",
            ):
                value = usage.get(key)
                if isinstance(value, int):
                    metadata[key] = value
        return metadata

    @classmethod
    def _map_transport_error(cls, error: JsonHttpTransportError) -> ProviderCallError:
        if error.status_code is not None:
            return cls._map_status(error.status_code, error.payload)
        return ProviderCallError(
            ProviderFailureKind.TRANSIENT,
            "Provider network transport failed",
            retryable=True,
        )

    @staticmethod
    def _map_status(status_code: int, payload: Mapping[str, Any]) -> ProviderCallError:
        message = _provider_error_message(payload)
        if status_code in {401, 403}:
            kind = ProviderFailureKind.AUTH
            retryable = False
        elif status_code == 429:
            kind = (
                ProviderFailureKind.QUOTA
                if "quota" in message.lower()
                else ProviderFailureKind.RATE_LIMIT
            )
            retryable = True
        elif status_code == 400:
            kind = ProviderFailureKind.INVALID_REQUEST
            retryable = False
        elif status_code >= 500:
            kind = ProviderFailureKind.TRANSIENT
            retryable = True
        else:
            kind = ProviderFailureKind.UNKNOWN
            retryable = False
        public_message = f"Provider request failed with HTTP {status_code}"
        if message:
            public_message = f"{public_message}: {message[:240]}"
        return ProviderCallError(
            kind,
            public_message,
            retryable=retryable,
            status_code=status_code,
        )


def _provider_error_message(payload: Mapping[str, Any]) -> str:
    error = payload.get("error")
    if not isinstance(error, dict):
        return ""
    message = error.get("message")
    return message if isinstance(message, str) else ""
