import pytest
from app.adapters.registry import available, get_adapter


def test_switch_between_providers_without_code_change():
    assert get_adapter({"active_model": "mock"}).name == "mock"
    assert "claude" in available()


def test_unknown_provider_fails_clearly():
    with pytest.raises(ValueError):
        get_adapter({"active_model": "nope"})


def test_claude_needs_server_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    pytest.importorskip("anthropic")
    with pytest.raises(RuntimeError):
        get_adapter({"active_model": "claude"})
