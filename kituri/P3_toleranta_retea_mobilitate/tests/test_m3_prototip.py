"""Teste de acceptanță pentru prototip (săptămâna 9): rute de rezervă, defecte,
recuperarea pe nivele. Sărite până le implementați. Rulare: pytest -q tests/test_m3_prototip.py"""
import networkx as nx
import numpy as np
import pandas as pd
import pytest

from sada.p3.graph_io import path_edges
from sada.p3.recovery import NetworkState


@pytest.fixture
def grid():
    G = nx.MultiDiGraph(nx.grid_2d_graph(6, 6).to_directed())
    G = nx.relabel_nodes(G, {n: f"{n[0]}_{n[1]}" for n in G.nodes})
    for u, v, k in G.edges(keys=True):
        G[u][v][k]["length"] = 100.0
    return G


@pytest.fixture
def pairs():
    return pd.DataFrame({"origin": ["0_0", "0_5", "2_2"], "destination": ["5_5", "5_0", "4_3"],
                         "priority": [True, False, False]})


def _skip(fn, *a, **k):
    try:
        return fn(*a, **k)
    except NotImplementedError as e:
        pytest.skip(f"nu e încă implementat: {e}")


def test_precompute_structure(grid, pairs):
    from sada.p3.routes import precompute
    R = _skip(precompute, grid, pairs)
    assert set(R) == {("0_0", "5_5"), ("0_5", "5_0"), ("2_2", "4_3")}
    for (o, d), r in R.items():
        assert r["primary"][0] == o and r["primary"][-1] == d
        assert r["backup"] is not None
        pe = {(u, v) for u, v, _ in path_edges(grid, r["primary"])}
        be = {(u, v) for u, v, _ in path_edges(grid, r["backup"])}
        assert not pe & be


def test_random_failures(grid):
    from sada.p3.failures import random_failures
    e = _skip(random_failures, grid, 0.1, np.random.default_rng(0))
    n = grid.number_of_edges()
    assert abs(len(e) - round(0.1 * n)) <= 1 and len(set(map(tuple, e))) == len(e)
    assert all(grid.has_edge(*x[:2]) for x in e)


def test_targeted_failures_follow_importance(grid):
    from sada.p3.failures import edge_importance, targeted_failures
    imp = edge_importance(grid, k=None)
    e = _skip(targeted_failures, grid, 0.05, imp, False)
    top = sorted(imp, key=imp.get, reverse=True)[: len(e)]
    assert [imp[tuple(x)] for x in e] == [imp[x] for x in top]


def test_recovery_switches_to_backup(grid, pairs):
    from sada.p3.recovery import HierarchicalRecovery
    from sada.p3.routes import precompute
    R = _skip(precompute, grid, pairs)
    st = NetworkState(grid, pairs, R)
    od = ("0_0", "5_5")
    st.fail(path_edges(grid, R[od]["primary"])[:1])          # cade prima muchie a rutei principale
    assert not st.route_ok(st.current[od])
    ctrl = HierarchicalRecovery({})
    _skip(ctrl.step, st, 1)
    assert st.route_ok(st.current[od]) and st.level[od] == 2
    assert st.served_share() == 1.0
