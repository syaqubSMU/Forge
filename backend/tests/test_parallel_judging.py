"""Judgments run in parallel; order, logging and failure handling must not depend on timing. Fakes only."""
import threading
import time

from app.adapters.base import ModelAdapter
from app.pipeline import run_match
from app.db import Database, DEFAULT_SETTINGS
from tests.test_pipeline import opp, factors_json

N = 12


class SlowAdapter(ModelAdapter):
    name = "slow"

    def __init__(self, delay=0.15, fail_on=()):
        super().__init__()
        self.delay, self.fail_on = delay, set(fail_on)
        self.active = self.peak = 0
        self._g = threading.Lock()

    def complete(self, system, prompt):
        with self._g:
            self.active += 1; self.peak = max(self.peak, self.active)
        try:
            time.sleep(self.delay)
            for bad in self.fail_on:
                if f"detail/{bad}]" in prompt:
                    raise RuntimeError("rate limited sk-ant-SECRET")
            src = next(l for l in prompt.splitlines() if "search-results-detail" in l).split("source_id: ")[1].rstrip("]")
            self._record({"input_tokens": 10, "output_tokens": 5})
            return factors_json(src=src)
        finally:
            with self._g:
                self.active -= 1


def go(adapter, workers, n=N):
    db = Database(":memory:")
    corpus = [opp(i, days=10 + i) for i in range(1, n + 1)]
    s = dict(DEFAULT_SETTINGS, judge_concurrency=workers, max_judgments=n)
    rid = db.create_run("v", "pi_name", "x", s, "r", adapter.name)
    t = time.time()
    out = run_match(db, rid, adapter, s, {"career_stage": "established", "lanes": ["photochemistry and flavin biology"]}, "q",
                    lister=lambda *a, **k: [dict(o) for o in corpus],
                    detailer=lambda ids, **k: ([dict(o) for o in corpus if o["source_record_id"] in ids], []))
    return out, time.time() - t, db, rid


def test_parallel_is_faster_and_bounded():
    a1 = SlowAdapter(); _, t1, *_ = go(a1, 1)
    a4 = SlowAdapter(); out, t4, *_ = go(a4, 4)
    assert t1 >= N * 0.15 * 0.9
    assert t4 < t1 / 2.5
    assert 1 < a4.peak <= 4 and a1.peak == 1
    assert len(out["results"]) == N and out["counters"]["judged"] == N


def test_results_and_log_order_do_not_depend_on_concurrency():
    o1 = go(SlowAdapter(0.01), 1)[0]; o8 = go(SlowAdapter(0.01), 8)[0]
    assert [r["url"] for r in o1["results"]] == [r["url"] for r in o8["results"]]


def test_one_failed_call_is_logged_and_does_not_sink_the_run():
    out, _, db, rid = go(SlowAdapter(0.01, fail_on=[3]), 4)
    assert out["counters"]["model_failures"] == 1 and len(out["results"]) == N - 1
    fails = db.q("SELECT * FROM run_source_failures WHERE run_id=?", (rid,))
    assert len(fails) == 1 and "RuntimeError" in dict(fails[0])["error"]
    assert "SECRET" not in str(dict(fails[0]))            # the exception text is never stored


def test_token_totals_are_exact_under_concurrency():
    a = SlowAdapter(0.005); go(a, 8, n=20)
    assert a.total_usage == {"input_tokens": 200, "output_tokens": 100} and len(a.call_log) == 20
