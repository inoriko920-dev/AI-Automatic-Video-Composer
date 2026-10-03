from __future__ import annotations

import pytest

from aavc.platform.credentials import MemoryCredentialStore
from aavc.providers.base import ProviderFailureKind
from aavc.providers.key_pool import KeyState, NoEligibleKeyError, ProviderKeyPool


def test_memory_credential_store_round_trip() -> None:
    store = MemoryCredentialStore()
    store.set_secret("gemini/key-001", "synthetic-secret")
    assert store.get_secret("gemini/key-001") == "synthetic-secret"
    store.delete_secret("gemini/key-001")
    with pytest.raises(KeyError):
        store.get_secret("gemini/key-001")


def test_key_pool_rotates_and_snapshot_never_contains_secret() -> None:
    now = [100.0]
    pool = ProviderKeyPool(
        ["gemini/key-001", "gemini/key-002"],
        cooldown_seconds=10.0,
        clock=lambda: now[0],
    )
    assert pool.acquire() == "gemini/key-001"
    pool.mark_failure("gemini/key-001", ProviderFailureKind.QUOTA)
    assert pool.acquire() == "gemini/key-002"
    snapshot_text = repr(pool.snapshot())
    assert "synthetic-secret" not in snapshot_text
    assert pool.snapshot()[0].state is KeyState.COOLDOWN
    now[0] = 111.0
    assert pool.snapshot()[0].state is KeyState.READY


def test_auth_failure_disables_key() -> None:
    pool = ProviderKeyPool(["gemini/key-001"])
    pool.mark_failure("gemini/key-001", ProviderFailureKind.AUTH)
    assert pool.snapshot()[0].state is KeyState.DISABLED
    with pytest.raises(NoEligibleKeyError):
        pool.acquire()


def test_pool_caps_at_one_hundred_references() -> None:
    pool = ProviderKeyPool([f"gemini/key-{index:03d}" for index in range(100)])
    with pytest.raises(ValueError):
        pool.add("gemini/key-100")
