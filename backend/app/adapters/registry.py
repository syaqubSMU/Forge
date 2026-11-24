"""Adapter registry: the admin setting `active_model` picks the adapter for the NEXT run (no redeploy).
Providers are registered by name; keys are read from the server environment per provider (never from the page)."""
from .mock import MockAdapter

PROVIDERS = {
    "mock": lambda: MockAdapter(["{}"]),
    "claude": lambda: __import__("app.adapters.claude", fromlist=["ClaudeAdapter"]).ClaudeAdapter(),
    # "oit-platform": register the institution-approved platform adapter here when OIT names it.
}


def available() -> list:
    return sorted(PROVIDERS)


def get_adapter(settings: dict):
    """Return the adapter named by settings['active_model']; fail clearly if unknown."""
    name = settings.get("active_model", "mock")
    if name not in PROVIDERS:
        raise ValueError(f"Unknown model provider '{name}'. Available: {', '.join(available())}")
    return PROVIDERS[name]()
