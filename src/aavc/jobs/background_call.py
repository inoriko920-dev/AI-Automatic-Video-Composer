from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock, Thread


@dataclass(frozen=True, slots=True)
class BackgroundCallSnapshot[T]:
    done: bool
    result: T | None = None
    error: Exception | None = None


class BackgroundCall[T]:
    """Run one blocking callable outside the GUI thread and expose a pollable snapshot."""

    def __init__(self, work: Callable[[], T]) -> None:
        self._work = work
        self._lock = Lock()
        self._started = False
        self._done = False
        self._result: T | None = None
        self._error: Exception | None = None
        self._thread: Thread | None = None

    @property
    def started(self) -> bool:
        with self._lock:
            return self._started

    def start(self) -> None:
        with self._lock:
            if self._started:
                raise RuntimeError("BackgroundCall hanya boleh dimulai sekali")
            self._started = True

        def runner() -> None:
            try:
                result = self._work()
            except Exception as error:  # worker boundary: surface failure to GUI poller
                with self._lock:
                    self._error = error
                    self._done = True
            else:
                with self._lock:
                    self._result = result
                    self._done = True

        thread = Thread(target=runner, name="aavc-background-call", daemon=True)
        self._thread = thread
        thread.start()

    def snapshot(self) -> BackgroundCallSnapshot[T]:
        with self._lock:
            return BackgroundCallSnapshot(
                done=self._done,
                result=self._result,
                error=self._error,
            )
