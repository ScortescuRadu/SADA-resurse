"""Teste de acceptanță pentru prototip (săptămâna 9): sistemul, regula simplă,
acoperirea. Testele pentru părțile TODO sunt sărite până le implementați.
Rulare: pytest -q tests/test_m3_prototip.py"""
import math

import numpy as np
import pandas as pd
import pytest

from sada.p4.system import TransitSystem

CTRL = {"window_min": 15, "overload": 0.85, "underuse": 0.30, "max_headway_min": 20,
        "coverage_radius_m": 400, "coverage_headway_min": 20}


def small_system():
    routes = ["A", "B", "C"]
    trips = {"A": 2.0, "B": 3.0, "C": 3.0}
    vh = {"A": 1.0, "B": 0.5, "C": 0.8}
    cap = {r: 100.0 for r in routes}
    demand = {("A", 0): 250.0, ("B", 0): 60.0, ("C", 0): 150.0}
    return TransitSystem(routes, trips, vh, cap, demand)


def test_system_basics():
    s = small_system()
    assert math.isclose(s.used_vehicle_hours(), 2 * 1.0 + 3 * 0.5 + 3 * 0.8)
    assert math.isclose(s.load_factor("A"), 1.25) and math.isclose(s.headway_min("B"), 5.0)
    s.move_trip("B", "A", 1)                       # 0,5 ore-vehicul de pe B pe A
    assert math.isclose(s.used_vehicle_hours(), s.budget_vh)


def test_rule_moves_capacity_to_overloaded_line_within_budget():
    from sada.p4.controller import SimpleRuleController
    s = small_system()
    ctrl = SimpleRuleController(CTRL)
    try:
        ctrl.step(s, 0)
    except NotImplementedError:
        pytest.skip("SimpleRuleController nu e încă implementat")
    assert s.trips["A"] > 2.0, "linia supraîncărcată n-a primit curse"
    assert s.used_vehicle_hours() <= s.budget_vh + 1e-9, "bugetul de ore-vehicul e depășit"
    assert all(s.headway_min(r) <= CTRL["max_headway_min"] for r in s.routes), "o linie a depășit intervalul maxim"
    assert len(ctrl.k.history) == 1


def test_coverage_share_geometry():
    from sada.p4.coverage import coverage_share
    pop = pd.DataFrame({"x_m": [0, 300, 1000], "y_m": [0, 0, 0], "population": [100, 50, 50]})
    stops = pd.DataFrame({"x_m": [0.0], "y_m": [0.0]})
    try:
        share = coverage_share(pop, stops, 400.0)
    except NotImplementedError:
        pytest.skip("coverage_share nu e încă implementat")
    assert math.isclose(share, 150 / 200)
