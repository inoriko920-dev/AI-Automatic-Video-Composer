from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum

from aavc.providers.base import ProviderFailureKind


class KeyState(str, Enum):
    READY = "ready"
    COOLDOWN = "cooldown"
    DISABLED = "disabled"


@dataclass(slots=True)
class _KeyRecord:
    reference: str
    state: KeyState = KeyState.READY
    cooldown_until: float = 0.0
    failures: int = 0


@dataclass(frozen=True, slots=True)
class KeySnapshot:
    reference: str
    state: KeyState
    cooldown_until: float
    failures: int


class NoEligibleKeyError(RuntimeError):
    pass


class ProviderKeyPool:
    def __init__(
        self,
        references: Iterable[str] = (),
        *,
        max_keys: int = 100,
        cooldown_seconds: float = 60.0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if max_keys < 1:
            raise ValueError("max_keys must be positive")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must not be negative")
        self._max_keys = max_keys
        self._cooldown_seconds = cooldown_seconds
        self._clock = clock
        self._records: list[_KeyRecord] = []
        self._cursor = 0
        for reference in references:
            self.add(reference)

    def add(self, reference: str) -> None:
        clean = reference.strip()
        if not clean or clean != reference:
            raise ValueError("key reference must be a non-empty trimmed string")
        if any(record.reference == reference for record in self._records):
            return
        if len(self._records) >= self._max_keys:
            raise ValueError(f"key pool supports at most {self._max_keys} references")
        self._records.append(_KeyRecord(reference=reference))

    def acquire(self) -> str:
        if not self._records:
            raise NoEligibleKeyError("provider key pool is empty")
        now = self._clock()
        self._refresh(now)
        total = len(self._records)
        for offset in range(total):
            index = (self._cursor + offset) % total
            record = self._records[index]
            if record.state is KeyState.READY:
                self._cursor = (index + 1) % total
                return record.reference
        raise NoEligibleKeyError("provider key pool has no eligible key")

    def mark_success(self, reference: str) -> None:
        record = self._find(reference)
        record.state = KeyState.READY
        record.cooldown_until = 0.0
        record.failures = 0

    def mark_failure(self, reference: str, kind: ProviderFailureKind) -> None:
        record = self._find(reference)
        record.failures += 1
        if kind is ProviderFailureKind.AUTH:
            record.state = KeyState.DISABLED
            record.cooldown_until = 0.0
            return
        if kind in {
            ProviderFailureKind.RATE_LIMIT,
            ProviderFailureKind.QUOTA,
            ProviderFailureKind.TRANSIENT,
        }:
            record.state = KeyState.COOLDOWN
            multiplier = min(record.failures, 5)
            record.cooldown_until = self._clock() + self._cooldown_seconds * multiplier

    def enable(self, reference: str) -> None:
        record = self._find(reference)
        record.state = KeyState.READY
        record.cooldown_until = 0.0
        record.failures = 0

    def snapshot(self) -> tuple[KeySnapshot, ...]:
        now = self._clock()
        self._refresh(now)
        return tuple(
            KeySnapshot(
                reference=record.reference,
                state=record.state,
                cooldown_until=record.cooldown_until,
                failures=record.failures,
            )
            for record in self._records
        )

    def __len__(self) -> int:
        return len(self._records)

    def _refresh(self, now: float) -> None:
        for record in self._records:
            if record.state is KeyState.COOLDOWN and record.cooldown_until <= now:
                record.state = KeyState.READY
                record.cooldown_until = 0.0

    def _find(self, reference: str) -> _KeyRecord:
        for record in self._records:
            if record.reference == reference:
                return record
        raise KeyError(reference)
