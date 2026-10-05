from __future__ import annotations

import time

from aavc.jobs.background_call import BackgroundCall
from aavc.presentation.windows.ai_native_motion_window import AiNativeMotionMainWindow
from aavc.presentation.windows.background_work_window import BackgroundWorkMainWindow


def _wait(call: BackgroundCall[object], timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if call.snapshot().done:
            return
        time.sleep(0.01)
    raise AssertionError("background call did not finish in time")


def test_background_runtime_preserves_ai_native_motion_layer() -> None:
    assert issubclass(BackgroundWorkMainWindow, AiNativeMotionMainWindow)


def test_background_call_returns_result_without_blocking_caller() -> None:
    call: BackgroundCall[object] = BackgroundCall(lambda: {"ok": True})
    call.start()
    _wait(call)

    snapshot = call.snapshot()
    assert snapshot.done is True
    assert snapshot.result == {"ok": True}
    assert snapshot.error is None


def test_background_call_surfaces_worker_error() -> None:
    def fail() -> object:
        raise ValueError("render failed")

    call: BackgroundCall[object] = BackgroundCall(fail)
    call.start()
    _wait(call)

    snapshot = call.snapshot()
    assert snapshot.done is True
    assert snapshot.result is None
    assert isinstance(snapshot.error, ValueError)
    assert str(snapshot.error) == "render failed"


def test_background_call_cannot_start_twice() -> None:
    call: BackgroundCall[object] = BackgroundCall(lambda: 1)
    call.start()
    try:
        call.start()
    except RuntimeError as error:
        assert "sekali" in str(error)
    else:
        raise AssertionError("second start should fail")
    _wait(call)
