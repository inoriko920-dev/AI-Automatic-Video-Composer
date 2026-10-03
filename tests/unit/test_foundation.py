from pathlib import Path

from aavc import __version__
from aavc.bootstrap.composition_root import build_foundation_services
from aavc.bootstrap.startup import FOUNDATION_SMOKE_TOKEN, main


def test_package_version_matches_release_candidate() -> None:
    assert __version__ == "0.1.0rc1"


def test_composition_root_builds_without_qt() -> None:
    services = build_foundation_services()
    assert services.app_name == "AI Automatic Video Composer"
    assert isinstance(services.paths.executable_dir, Path)


def test_foundation_smoke_mode(capsys) -> None:
    assert main(["--foundation-smoke"]) == 0
    assert FOUNDATION_SMOKE_TOKEN in capsys.readouterr().out


def test_foundation_smoke_can_write_marker(tmp_path: Path) -> None:
    marker = tmp_path / "portable-smoke.txt"
    assert main(["--foundation-smoke", "--foundation-smoke-file", str(marker)]) == 0
    assert marker.read_text(encoding="utf-8") == FOUNDATION_SMOKE_TOKEN
