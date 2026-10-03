from __future__ import annotations

import sys

import pytest

from aavc.platform.process_runner import ProcessLaunchError, ProcessRunner, ProcessTimeoutError


def test_process_runner_returns_completed_result() -> None:
    result = ProcessRunner().run([sys.executable, "-c", "print('ok')"], timeout_seconds=5.0)
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_process_runner_normalizes_timeout() -> None:
    with pytest.raises(ProcessTimeoutError):
        ProcessRunner().run(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            timeout_seconds=0.1,
        )


def test_process_runner_normalizes_launch_failure_without_arguments() -> None:
    with pytest.raises(ProcessLaunchError) as caught:
        ProcessRunner().run(["aavc-definitely-missing-executable-12345"])
    assert "aavc-definitely-missing-executable-12345" in str(caught.value)
