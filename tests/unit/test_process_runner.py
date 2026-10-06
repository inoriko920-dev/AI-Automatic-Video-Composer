from __future__ import annotations

import sys

from aavc.platform.process_runner import ProcessRunner, windows_command_line_units


def test_process_runner_replaces_undecodable_child_output() -> None:
    runner = ProcessRunner()
    result = runner.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.stderr.buffer.write(bytes([0x81])); sys.stderr.flush()",
        ]
    )

    assert result.returncode == 0
    assert isinstance(result.stderr, str)
    assert result.stderr



def test_windows_command_line_units_counts_utf16_and_nul() -> None:
    argv = ["ffmpeg.exe", "-i", "C:/video/😀 sample.png", "out.mp4"]

    import subprocess

    command_line = subprocess.list2cmdline(argv)
    expected = len(command_line.encode("utf-16-le")) // 2 + 1
    assert windows_command_line_units(argv) == expected
