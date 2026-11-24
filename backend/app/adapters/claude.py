import os

from .base import ModelAdapter

API_BASE = "https://api.anthropic.com"


class ClaudeAdapter(ModelAdapter):
    """Claude via the Anthropic API. The key comes from the server environment only (hard rule 4):
    never from the page, never returned by the API, never written to a log."""
    name = "claude"

    def __init__(self, model=None, max_tokens=1500, effort=None):
        super().__init__()
        import anthropic  # imported lazily so the test suite runs without the package
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set on the server. Add it to the cloud environment's "
                "variables and start a new session; variables are read at session start.")
        # This container sets ANTHROPIC_BASE_URL for Claude Code's own traffic. The SDK would inherit
        # it and send our calls somewhere else, so the real API base is set explicitly.
        self.client = anthropic.Anthropic(api_key=key, base_url=os.environ.get("FORGE_API_BASE", API_BASE))
        self.model = model or os.environ.get("FORGE_MODEL", "claude-opus-5-5")
        self.max_tokens = max_tokens
        self.effort = effort or os.environ.get("FORGE_EFFORT")

    def complete(self, system, prompt):
        kwargs = {"model": self.model, "max_tokens": self.max_tokens, "system": system,
                  "messages": [{"role": "user", "content": prompt}]}
        if self.effort:                      # low effort keeps thinking tokens down on the bulk screen
            kwargs["output_config"] = {"effort": self.effort}
        r = self.client.messages.create(**kwargs)
        u = getattr(r, "usage", None)
        self._record({"input_tokens": getattr(u, "input_tokens", 0) or 0,
                      "output_tokens": getattr(u, "output_tokens", 0) or 0})
        if getattr(r, "stop_reason", None) == "refusal":
            raise RuntimeError("the model declined this request")
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
