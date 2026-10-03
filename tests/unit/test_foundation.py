from pathlib import Path

from aavc import __version__
from aavc.bootstrap.composition_root import build_foundation_services
from aavc.bootstrap.startup import FOUNDATION_SMOKE_TOKEN, main


def test_package_version_is_foundation_version() -> None:
    assert __version__ == "0.0.0.dev11"


def test_composition_root_builds_without_qt() -> None:
    services = build_foundation_services()
    assert services.app_name == "AI Automatic Video Composer"
    assert isinstance(services.paths.executable_dir, Path)


def test_foundation_smoke_mode(capsys) -> None:
    assert main(["--foundation-smoke"]) == 0
    assert FOUNDATION_SMOKE_TOKEN in capsys.readouterr().out
