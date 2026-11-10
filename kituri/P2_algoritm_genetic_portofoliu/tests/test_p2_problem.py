"""Teste pentru partea gata făcută a temei P2 și teste de acceptanță pentru
algoritmul genetic (sărite până îl implementați). Rulare: pytest -q"""
import itertools
import json

import numpy as np
import pytest

from sada.p2.baselines import greedy, random_search
from sada.p2.dynamic import ChangeSchedule
from sada.p2.exact import solve_exact
from sada.p2.problem import Problem


@pytest.fixture
def small(tmp_path):
    rng = np.random.default_rng(0)
    n = 10
    items = [{"id": f"S{i}", "cost": float(c), "benefit": float(b), "equity": float(e)}
             for i, (c, b, e) in enumerate(zip(rng.integers(10, 100, n), rng.integers(5, 80, n), rng.integers(0, 20, n)))]
    items[3]["requires"] = "S2"
    path = tmp_path / "inst.json"
    path.write_text(json.dumps({"name": "t", "kind": "binary", "budget": 250.0, "items": items}))
    return Problem.from_json(path)


def brute(p):
    best = -np.inf
    for bits in itertools.product([0, 1], repeat=p.n):
        x = np.array(bits)
        if p.is_feasible(x):
            best = max(best, p.objective(x))
    return best


def test_exact_matches_bruteforce(small):
    x, v = solve_exact(small)
    assert small.is_feasible(x)
    assert np.isclose(v, brute(small))


def test_exact_after_changes(small):
    for ch in [{"type": "budget_scale", "factor": 0.7}, {"type": "remove_item", "id": "S1"},
               {"type": "weights", "w_benefit": 0.5, "w_equity": 0.5}]:
        small.apply_change(ch)
        x, v = solve_exact(small)
        assert np.isclose(v, brute(small))


def test_greedy_and_random_are_feasible(small):
    x, v, _ = greedy(small)
    assert small.is_feasible(x)
    x, v, n = random_search(small, 500, np.random.default_rng(1))
    assert x is not None and small.is_feasible(x) and n == 500


def test_schedule_applies_only_at_generation(small):
    s = ChangeSchedule([{"generation": 5, "type": "budget_scale", "factor": 0.5}])
    b0 = small.budget
    assert s.apply(small, 4) == [] and small.budget == b0
    s.apply(small, 5)
    assert small.budget == b0 * 0.5


def test_ga_beats_random_on_small(small):
    from sada.p2.ga import DynamicGA
    ga = DynamicGA(small, {"pop_size": 30, "tournament_k": 3, "p_crossover": 0.9,
                           "p_mut": None, "elitism": 1}, np.random.default_rng(0))
    try:
        h = ga.run(60)
    except NotImplementedError:
        pytest.skip("DynamicGA nu e încă implementat")
    best = [r for r in h if r["best_feasible"]][-1]["best_objective"]
    assert best >= 0.95 * brute(small)
