from __future__ import annotations

from aavc.providers.context_builder import ProviderContextBuilder, redact_secrets


def test_context_builder_removes_sensitive_metadata_and_redacts_inline_secret() -> None:
    builder = ProviderContextBuilder(max_chars=1000)
    result = builder.build(
        "Atur scene ini. api_key=very-secret",
        scene_id="Scene 08",
        asset_ids=["A014", "A015"],
        metadata={"title": "Demo", "api_key": "do-not-send", "token": "also-private"},
    )
    assert "very-secret" not in result
    assert "do-not-send" not in result
    assert "also-private" not in result
    assert "[REDACTED]" in result
    assert "A014, A015" in result
    assert "title: Demo" in result


def test_context_builder_truncates_to_budget() -> None:
    builder = ProviderContextBuilder(max_chars=256)
    result = builder.build("x" * 600)
    assert len(result) <= 256
    assert result.endswith("[CONTEXT_TRUNCATED]")


def test_redact_secrets_handles_token_assignment() -> None:
    assert redact_secrets("token: abc123") == "token=[REDACTED]"
