"""Teste de acceptanță pentru prototip (săptămâna 9): algoritmul genetic plus
controllerul. Sărite până le implementați. Rulare: pytest -q tests/test_m3_prototip.py"""
import json

import numpy as np
import pytest

from sada.p2.dynamic import ChangeSchedule
from sada.p2.problem import Problem

GA_CFG = {"pop_size": 40, "tournament_k": 3, "p_crossover": 0.9, "p_mut": None, "elitism": 2}
CTRL_CFG = {"n_sentinels": 5, "stagnation_generations": 30, "hypermutation_factor": 5,
            "hypermutation_generations": 10, "immigrants_frac": 0.2, "restart_frac": 0.5}


@pytest.fixture
def problem(tmp_path):
    rng = np.random.default_rng(5)
    n = 16
    items = [{"id": f"S{i}", "cost": float(c), "benefit": float(b), "equity": float(e)}
             for i, (c, b, e) in enumerate(zip(rng.integers(10, 100, n), rng.integers(5, 80, n), rng.integers(0, 20, n)))]
    path = tmp_path / "p.json"
    path.write_text(json.dumps({"name": "m3", "kind": "binary", "budget": 400.0, "items": items}))
    return Problem.from_json(path)


def _run(problem, response, gens=120):
    from sada.p2.controller import DynamicGAController
    from sada.p2.ga import DynamicGA
    ga = DynamicGA(problem, GA_CFG, np.random.default_rng(0))
    ctrl = DynamicGAController({**CTRL_CFG, "response": response})
    sched = ChangeSchedule([{"generation": 60, "type": "budget_scale", "factor": 0.6}])
    try:
        h = ga.run(gens, sched, ctrl)
    except NotImplementedError:
        pytest.skip("DynamicGA sau DynamicGAController nu e încă implementat")
    return ga, ctrl, h


def test_change_is_detected_quickly(problem):
    _, ctrl, _ = _run(problem, "hypermutation")
    reactions = [e["t"] for e in ctrl.k.history if e.get("action") is not None and e["t"] >= 60]
    assert reactions and reactions[0] <= 63, "schimbarea de la generația 60 n-a fost detectată în 3 generații"


def test_no_false_alarm_before_change(problem):
    _, ctrl, _ = _run(problem, "hypermutation")
    early = [e for e in ctrl.k.history if e["t"] < 60 and "schimb" in str(e.get("assessment", "")).lower()]
    assert not early, "controllerul a raportat o schimbare înainte să existe una"


def test_hypermutation_raises_then_restores_mutation(problem):
    ga, _, h = _run(problem, "hypermutation")
    after = [r["p_mut"] for r in h if 60 <= r["generation"] <= 70]
    late = [r["p_mut"] for r in h if r["generation"] >= 100]
    assert max(after) > ga.base_p_mut, "rata de mutație nu crește după schimbare"
    assert np.isclose(late[-1], ga.base_p_mut), "rata de mutație nu revine la valoarea de bază"


def test_best_solution_feasible_after_change(problem):
    _, _, h = _run(problem, "immigrants")
    assert h[-1]["best_feasible"], "cel mai bun individ la final nu respectă bugetul redus"
