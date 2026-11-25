import os
import time

from .base import ModelAdapter

API_BASE = "https://api.anthropic.com"

# The cloud environment refuses variable names that would override the session's own credentials,
# so ANTHROPIC_API_KEY often cannot be saved there. Any of these is accepted, first one wins.
# Rate limits (429), overload (529) and dropped connections are retried by the SDK with exponential backoff,
# honouring the server's retry-after header. Parallel judging relies on this.
MAX_RETRIES = int(os.environ.get("FORGE_MODEL_RETRIES", "6"))
TIMEOUT_S = float(os.environ.get("FORGE_MODEL_TIMEOUT_S", "120"))
KEY_VARS = ("FORGE_MODEL_KEY", "FORGE_API_KEY", "SIGNAL_MODEL_KEY", "ANTHROPIC_API_KEY")


def find_key(env=None):
    env = os.environ if env is None else env
    for name in KEY_VARS:
        value = (env.get(name) or "").strip()
        if value:
            return name, value
    return None, None


class ClaudeAdapter(ModelAdapter):
    """Claude via the Anthropic API. The key comes from the server environment only (hard rule 4):
    never from the page, never returned by the API, never written to a log."""
    name = "claude"

    def __init__(self, model=None, max_tokens=1500, effort=None):
        super().__init__()
        import anthropic  # imported lazily so the test suite runs without the package
        self.key_var, key = find_key()
        if not key:
            raise RuntimeError(
                "No model key on the server. Set one of %s in the cloud environment's variables, "
                "then start a new session; variables are read at session start."
                % ", ".join(KEY_VARS))
        # This container sets ANTHROPIC_BASE_URL for Claude Code's own traffic. The SDK would inherit
        # it and send our calls somewhere else, so the real API base is set explicitly.
        self.client = anthropic.Anthropic(api_key=key, base_url=os.environ.get("FORGE_API_BASE", API_BASE),
                                      max_retries=MAX_RETRIES, timeout=TIMEOUT_S)
        self.model = model or os.environ.get("FORGE_MODEL", "claude-opus-5-5")
        self.max_tokens = max_tokens
        self.effort = effort or os.environ.get("FORGE_EFFORT")

    def complete(self, system, prompt):
        kwargs = {"model": self.model, "max_tokens": self.max_tokens, "system": system,
                  "messages": [{"role": "user", "content": prompt}]}
        if self.effort:                      # low effort keeps thinking tokens down on the bulk screen
            kwargs["output_config"] = {"effort": self.effort}
        t = time.time()
        r = self.client.messages.create(**kwargs)
        u = getattr(r, "usage", None)
        self._record({"input_tokens": getattr(u, "input_tokens", 0) or 0,
                      "output_tokens": getattr(u, "output_tokens", 0) or 0,
                      "seconds": round(time.time() - t, 2), "stop_reason": getattr(r, "stop_reason", None)})
        if getattr(r, "stop_reason", None) == "refusal":
            raise RuntimeError("the model declined this request")
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
