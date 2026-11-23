from .base import ModelAdapter


class MockAdapter(ModelAdapter):
    """Deterministic stand-in for tests. `responses` is a list of raw strings returned in order."""
    name = "mock"

    def __init__(self, responses):
        self.responses, self.calls = list(responses), 0

    def complete(self, system, prompt):
        r = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return r
