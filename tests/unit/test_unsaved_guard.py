from aavc.presentation.windows.guarded_main_window import resolve_unsaved_choice


def test_clean_project_never_blocks_destructive_action() -> None:
    assert resolve_unsaved_choice(False, "cancel")
    assert resolve_unsaved_choice(False, "save", save_succeeded=False)


def test_dirty_project_allows_discard_and_blocks_cancel() -> None:
    assert resolve_unsaved_choice(True, "discard")
    assert not resolve_unsaved_choice(True, "cancel")


def test_dirty_project_only_allows_save_when_persistence_succeeds() -> None:
    assert resolve_unsaved_choice(True, "save", save_succeeded=True)
    assert not resolve_unsaved_choice(True, "save", save_succeeded=False)
