from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from aavc.platform.credentials import CredentialStore
from aavc.providers.base import (
    ProviderAdapter,
    ProviderCallError,
    ProviderFailureKind,
    ProviderRequest,
    ProviderResponse,
)
from aavc.providers.key_pool import KeySnapshot, NoEligibleKeyError, ProviderKeyPool


class ProviderConfigurationError(RuntimeError):
    pass


class ProviderExhaustedError(RuntimeError):
    def __init__(self, provider: str, kind: ProviderFailureKind | None = None) -> None:
        suffix = "" if kind is None else f"; last failure={kind.value}"
        super().__init__(f"Provider '{provider}' exhausted eligible credentials{suffix}")
        self.provider = provider
        self.kind = kind


class ProviderManager:
    def __init__(self, credential_store: CredentialStore) -> None:
        self._credential_store = credential_store
        self._adapters: dict[str, ProviderAdapter] = {}
        self._pools: dict[str, ProviderKeyPool] = {}

    def register(self, adapter: ProviderAdapter, pool: ProviderKeyPool) -> None:
        name = adapter.name.strip().lower()
        if not name:
            raise ValueError("provider adapter name must not be empty")
        self._adapters[name] = adapter
        self._pools[name] = pool

    def generate(
        self,
        provider: str,
        request: ProviderRequest,
        *,
        max_attempts: int | None = None,
    ) -> ProviderResponse:
        name = provider.strip().lower()
        adapter = self._adapters.get(name)
        pool = self._pools.get(name)
        if adapter is None or pool is None:
            raise ProviderConfigurationError(f"Provider '{name}' is not registered")
        attempts = len(pool) if max_attempts is None else max_attempts
        if attempts < 1:
            raise ValueError("max_attempts must be positive")

        last_kind: ProviderFailureKind | None = None
        for _ in range(attempts):
            try:
                reference = pool.acquire()
            except NoEligibleKeyError:
                break

            try:
                secret = self._credential_store.get_secret(reference)
            except KeyError:
                # Missing/invalid credentials may legitimately fall back to a
                # configured backup reference. This is not quota aggregation.
                pool.mark_failure(reference, ProviderFailureKind.AUTH)
                last_kind = ProviderFailureKind.AUTH
                continue

            try:
                response = adapter.generate(request, api_key=secret)
            except ProviderCallError as exc:
                last_kind = exc.kind
                pool.mark_failure(reference, exc.kind)
                if exc.kind is ProviderFailureKind.AUTH:
                    # Authentication failure disables the unusable credential;
                    # a later loop iteration may use an explicit backup.
                    continue
                # Rate-limit, quota, transient, invalid-request and unknown
                # failures are surfaced. Never hop credentials to evade service
                # limits or account policy.
                raise
            finally:
                secret = ""

            pool.mark_success(reference)
            return replace(response, key_ref=reference)

        raise ProviderExhaustedError(name, last_kind)

    def snapshots(self) -> Mapping[str, tuple[KeySnapshot, ...]]:
        return {name: pool.snapshot() for name, pool in self._pools.items()}
