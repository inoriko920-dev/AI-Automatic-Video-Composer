from __future__ import annotations

import pytest

from aavc.platform.credentials import InMemoryCredentialStore
from aavc.presentation.windows.ai_menu_window import (
    AiMenuMainWindow,
    configured_gemini_slots,
    gemini_credential_reference,
    gemini_credentials_supported,
    gemini_status_text,
)
from aavc.presentation.windows.animation_menu_window import AnimationMenuMainWindow


def test_ai_menu_preserves_current_animation_runtime_layer() -> None:
    assert issubclass(AiMenuMainWindow, AnimationMenuMainWindow)


def test_gemini_credential_reference_supports_exactly_100_slots() -> None:
    assert gemini_credential_reference(1) == "gemini-slot-001"
    assert gemini_credential_reference(100) == "gemini-slot-100"
    with pytest.raises(ValueError):
        gemini_credential_reference(0)
    with pytest.raises(ValueError):
        gemini_credential_reference(101)


def test_secure_gemini_store_is_windows_only() -> None:
    assert gemini_credentials_supported("win32") is True
    assert gemini_credentials_supported("linux") is False
    assert gemini_credentials_supported("darwin") is False


def test_configured_slots_and_status_never_expose_secret_values() -> None:
    credentials = InMemoryCredentialStore()
    secret_one = "AIzaSYNTHETIC_SECRET_ONE_123456789"
    secret_three = "AIzaSYNTHETIC_SECRET_THREE_987654321"
    credentials.set_secret(gemini_credential_reference(1), secret_one)
    credentials.set_secret(gemini_credential_reference(3), secret_three)

    slots = configured_gemini_slots(credentials)
    status = gemini_status_text(slots)

    assert slots == (1, 3)
    assert "2/100" in status
    assert "1, 3" in status
    assert secret_one not in status
    assert secret_three not in status


def test_empty_gemini_status_contains_no_credential_material() -> None:
    status = gemini_status_text(())
    assert "Belum ada API key Gemini" in status
    assert "100 slot" in status
