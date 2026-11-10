"""Teste de acceptanță pentru RingRoad. Sunt sărite (skipped) până implementați
RingRoad.step; după aceea trebuie să treacă toate.  Rulare: pytest -q"""
import numpy as np
import pytest

from sada.p1.nasch import RingRoad


def make(**kw):
    road = RingRoad(**{"length": 300, "density": 0.1, "vmax": 2, "p": 0.0, "rng": np.random.default_rng(0), **kw})
    try:
        road.step()
    except NotImplementedError:
        pytest.skip("RingRoad.step nu e încă implementat")
    return road


def run(road, steps):
    for _ in range(steps):
        road.step()
    return road


def test_vehicle_count_conserved():
    road = run(make(density=0.3, p=0.3), 200)
    assert road.n == int(round(0.3 * 300))
    assert len(np.unique(road.pos)) == road.n, "două vehicule în aceeași celulă"


def test_free_flow_reaches_vmax():
    road = run(make(density=0.05, p=0.0), 300)
    assert np.all(road.vel == 2)


def test_no_collisions_and_sorted():
    road = make(density=0.5, p=0.4)
    for _ in range(300):
        road.step()
        assert np.all(np.diff(road.pos) > 0)
        assert np.all(road.gaps() >= 0)


def test_speeds_within_bounds():
    road = run(make(density=0.3, p=0.5), 200)
    assert road.vel.min() >= 0 and road.vel.max() <= 2


def test_jam_at_high_density():
    road = run(make(density=0.6, p=0.3), 300)
    assert road.mean_speed < 1.0


@pytest.mark.parametrize("rule", ["vdr", "sts"])
def test_variants_lower_flow_than_nasch_in_congestion(rule):
    def mean_flow(r):
        road = run(make(density=0.3, p=0.2, p0=0.7, rule=r, rng=np.random.default_rng(3)), 300)
        return np.mean([run(road, 1).flow for _ in range(300)])
    assert mean_flow(rule) <= mean_flow("nasch") + 1e-9
