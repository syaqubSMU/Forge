import os

from .base import ModelAdapter


class ClaudeAdapter(ModelAdapter):
    """Claude via the Anthropic API. The key comes from the server environment only (hard rule 4)."""
    name = "claude"

    def __init__(self, model=None, max_tokens=1500):
        import anthropic  # imported lazily so tests run without the package
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set on the server")
        self.client = anthropic.Anthropic(api_key=key)
        self.model = model or os.environ.get("FORGE_MODEL", "claude-sonnet-5-5")
        self.max_tokens = max_tokens

    def complete(self, system, prompt):
        r = self.client.messages.create(model=self.model, max_tokens=self.max_tokens, system=system,
                                        messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
