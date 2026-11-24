import pytest
from app.adapters.registry import available, get_adapter


def test_switch_between_providers_without_code_change():
    assert get_adapter({"active_model": "mock"}).name == "mock"
    assert "claude" in available()


def test_unknown_provider_fails_clearly():
    with pytest.raises(ValueError):
        get_adapter({"active_model": "nope"})


def test_claude_needs_server_key(monkeypatch):
    from app.adapters.claude import KEY_VARS
    for name in KEY_VARS:                      # every accepted name, so a real key in the environment cannot leak in
        monkeypatch.delenv(name, raising=False)
    pytest.importorskip("anthropic")
    with pytest.raises(RuntimeError):
        get_adapter({"active_model": "claude"})


def test_any_accepted_key_variable_name_works(monkeypatch):
    """The cloud environment refuses ANTHROPIC_API_KEY as a variable name, so the adapter
    accepts several alternatives. The value itself is never logged or returned."""
    from app.adapters.claude import KEY_VARS, find_key
    for name in KEY_VARS:
        env = {name: "test-value"}
        assert find_key(env) == (name, "test-value")
    assert find_key({}) == (None, None)
    assert find_key({"FORGE_MODEL_KEY": "  padded  "}) == ("FORGE_MODEL_KEY", "padded")
    assert find_key({"FORGE_MODEL_KEY": "   "}) == (None, None)      # whitespace is not a key


def test_missing_key_message_names_the_variables_but_no_value(monkeypatch):
    import pytest as _p
    from app.adapters.claude import KEY_VARS, ClaudeAdapter
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    _p.importorskip("anthropic")
    with _p.raises(RuntimeError) as e:
        ClaudeAdapter()
    assert "FORGE_MODEL_KEY" in str(e.value)
