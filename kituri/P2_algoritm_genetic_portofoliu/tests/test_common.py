"""Teste pentru partea comună. Rulare: pytest -q"""
import numpy as np

from sada.mapek import Controller, FixedController
from sada.stats import a12, fmt, summarize


def test_fmt_uses_comma():
    assert fmt(124.33, 8.71) == "124,3 ± 8,7"


def test_a12_bounds():
    assert a12([1, 2, 3], [1, 2, 3]) == 0.5
    assert a12([10, 11], [1, 2]) == 1.0


def test_summarize_mean_std():
    import pandas as pd
    df = pd.DataFrame({"scenario": ["s"] * 4, "variant": ["v"] * 4, "m": [1, 2, 3, 4]})
    r = summarize(df, ["m"]).iloc[0]
    assert r["m_mean"] == 2.5 and np.isclose(r["m_std"], np.std([1, 2, 3, 4], ddof=1))


def test_fixed_controller_does_nothing():
    c = FixedController()
    assert c.step(system=None, t=0) is None
    assert c.k.history == []


def test_controller_logs_actions(tmp_path):
    class Toy(Controller):
        def monitor(self, s, t): return {"x": t}
        def analyze(self, m, t): return m["x"] > 1
        def plan(self, a, t): return "act" if a else None
        def execute(self, s, a, t): pass

    c = Toy(log_path=tmp_path / "log.jsonl")
    for t in range(4):
        c.step(None, t)
    assert len(c.k.history) == 2
    assert len((tmp_path / "log.jsonl").read_text().splitlines()) == 2
