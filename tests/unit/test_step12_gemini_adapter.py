from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from aavc.providers.adapters.gemini import GeminiRestAdapter
from aavc.providers.base import ProviderCallError, ProviderFailureKind, ProviderRequest
from aavc.providers.http import HttpResult, JsonHttpTransportError


class FakeTransport:
    def __init__(self, result: HttpResult | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.url = ""
        self.payload: Mapping[str, Any] = {}
        self.headers: Mapping[str, str] = {}

    def post_json(
        self,
        url: str,
        payload: Mapping[str, Any],
        *,
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResult:
        del timeout_s
        self.url = url
        self.payload = payload
        self.headers = headers
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("fake transport requires result or error")
        return self.result


def test_gemini_adapter_uses_header_key_and_parses_text() -> None:
    transport = FakeTransport(
        HttpResult(
            200,
            {
                "candidates": [{"content": {"parts": [{"text": "Halo"}, {"text": " dunia"}]}}],
                "usageMetadata": {"totalTokenCount": 12},
            },
        )
    )
    adapter = GeminiRestAdapter(transport)
    response = adapter.generate(
        ProviderRequest(prompt="Uji", model="gemini-test", temperature=0.2),
        api_key="synthetic-secret",
    )
    assert response.text == "Halo dunia"
    assert response.metadata["totalTokenCount"] == 12
    assert "synthetic-secret" not in transport.url
    assert transport.headers["x-goog-api-key"] == "synthetic-secret"
    assert transport.payload["generationConfig"] == {"temperature": 0.2}


def test_gemini_adapter_maps_quota_without_echoing_key() -> None:
    transport = FakeTransport(
        error=JsonHttpTransportError(
            "HTTP 429",
            status_code=429,
            payload={"error": {"message": "Quota exceeded"}},
        )
    )
    adapter = GeminiRestAdapter(transport)
    with pytest.raises(ProviderCallError) as caught:
        adapter.generate(
            ProviderRequest(prompt="Uji", model="gemini-test"),
            api_key="synthetic-secret",
        )
    assert caught.value.kind is ProviderFailureKind.QUOTA
    assert caught.value.retryable is True
    assert "synthetic-secret" not in str(caught.value)
