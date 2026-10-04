from __future__ import annotations

from aavc.presentation.windows.main_window import ensure_project_suffix, pending_feature_message


def test_pending_feature_message_names_feature_and_preserves_project() -> None:
    title, message = pending_feature_message("Impor Media")

    assert title == "Fitur belum terhubung"
    assert "Impor Media" in message
    assert "Tidak ada perubahan proyek yang dilakukan." in message


def test_pending_feature_message_is_reusable_for_other_actions() -> None:
    _title, message = pending_feature_message("Rekam Narasi")

    assert "Rekam Narasi" in message


def test_ensure_project_suffix_appends_only_when_needed() -> None:
    assert ensure_project_suffix("demo") == "demo.aavcproj"
    assert ensure_project_suffix("demo.aavcproj") == "demo.aavcproj"
    assert ensure_project_suffix("demo.AAVCPROJ") == "demo.AAVCPROJ"
