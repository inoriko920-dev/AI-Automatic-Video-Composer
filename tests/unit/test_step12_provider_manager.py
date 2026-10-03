from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from aavc.platform.credentials import MemoryCredentialStore
from aavc.providers.base import (
    ProviderCallError,
    ProviderFailureKind,
    ProviderRequest,
    ProviderResponse,
)
from aavc.providers.key_pool import KeyState, ProviderKeyPool
from aavc.providers.manager import ProviderExhaustedError, ProviderManager


@dataclass
class FakeAdapter:
    name: str = "gemini"
    outcomes: list[object] = field(default_factory=list)
    seen_keys: list[str] = field(default_factory=list)

    def generate(self, request: ProviderRequest, *, api_key: str) -> ProviderResponse:
        self.seen_keys.append(api_key)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        assert isinstance(outcome, str)
        return ProviderResponse(text=outcome, provider=self.name, model=request.model)


def test_manager_rotates_after_quota_failure() -> None:
    store = MemoryCredentialStore()
    store.set_secret("gemini/key-001", "secret-one")
    store.set_secret("gemini/key-002", "secret-two")
    adapter = FakeAdapter(
        outcomes=[
            ProviderCallError(
                ProviderFailureKind.QUOTA,
                "quota",
                retryable=True,
                status_code=429,
            ),
            "ok",
        ]
    )
    pool = ProviderKeyPool(["gemini/key-001", "gemini/key-002"])
    manager = ProviderManager(store)
    manager.register(adapter, pool)

    response = manager.generate("gemini", ProviderRequest(prompt="hi", model="test"))
    assert response.text == "ok"
    assert response.key_ref == "gemini/key-002"
    assert adapter.seen_keys == ["secret-one", "secret-two"]
    assert pool.snapshot()[0].state is KeyState.COOLDOWN


def test_manager_disables_missing_credential_and_exhausts_cleanly() -> None:
    store = MemoryCredentialStore()
    adapter = FakeAdapter(outcomes=[])
    pool = ProviderKeyPool(["gemini/key-001"])
    manager = ProviderManager(store)
    manager.register(adapter, pool)

    with pytest.raises(ProviderExhaustedError) as caught:
        manager.generate("gemini", ProviderRequest(prompt="hi", model="test"))
    assert caught.value.kind is ProviderFailureKind.AUTH
    assert "secret" not in str(caught.value).lower()
    assert pool.snapshot()[0].state is KeyState.DISABLED
