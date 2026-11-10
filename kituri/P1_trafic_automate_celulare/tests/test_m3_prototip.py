"""Teste de acceptanță pentru prototip (săptămâna 9). Sunt sărite până
implementați coridorul și controllerul. Rulare: pytest -q tests/test_m3_prototip.py"""
import numpy as np
import pytest

from sada.config import load_config


def _cfg():
    cfg = load_config("config/default.yaml")
    cfg["controller"].update(enter_dense=25, exit_dense=20, enter_jam=60, exit_jam=50, window_s=60)
    return cfg


def test_corridor_moves_vehicles_and_respects_speed_limit():
    from sada.p1.corridor import Corridor
    cfg = _cfg()
    try:
        cor = Corridor(cfg, inflow_veh_h=600, rng=np.random.default_rng(0))
        for _ in range(1200):
            cor.step()
    except NotImplementedError:
        pytest.skip("Corridor nu e încă implementat")
    m = cfg["model"]
    assert cor.exit_count > 0, "niciun vehicul n-a ieșit din coridor în 20 de minute"
    v_max_m_s = m["vmax"] * m["cell_m"] / m["dt_s"]
    assert min(cor.travel_times) >= m["length_m"] / v_max_m_s - 1e-6, "un vehicul a mers mai repede decât vmax"


def test_segment_measurements_shape():
    from sada.p1.corridor import Corridor
    cfg = _cfg()
    try:
        cor = Corridor(cfg, inflow_veh_h=900, rng=np.random.default_rng(1))
        for _ in range(300):
            cor.step()
        meas = cor.segment_measurements()
    except NotImplementedError:
        pytest.skip("Corridor nu e încă implementat")
    for k in ("density_veh_km", "speed_km_h"):
        assert len(np.asarray(meas[k])) == cor.n_segments


class FakeCorridor:
    """Un coridor fals, foarte aglomerat pe tronsonul 2, ca să testăm doar controllerul."""
    n_segments = 5

    def __init__(self):
        self.segment_rule = ["nasch"] * 5
        self.calls = []

    def segment_measurements(self):
        d = np.array([10.0, 12.0, 90.0, 11.0, 9.0])
        v = np.array([50.0, 48.0, 5.0, 49.0, 51.0])
        return {"density_veh_km": d, "speed_km_h": v}

    def set_rule(self, segment, rule):
        self.calls.append((segment, rule))
        self.segment_rule[segment] = rule


def test_controller_reacts_on_jammed_segment_and_logs():
    from sada.p1.controller import TrafficController
    cor = FakeCorridor()
    ctrl = TrafficController(_cfg()["controller"])
    try:
        for t in range(0, 600, 60):
            ctrl.step(cor, t)
    except NotImplementedError:
        pytest.skip("TrafficController nu e încă implementat")
    assert any(seg == 2 for seg, _ in cor.calls), "controllerul n-a schimbat nimic pe tronsonul blocat"
    assert len(ctrl.k.history) > 0, "deciziile nu apar în jurnal"
