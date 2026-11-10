"""Teste pentru partea gata făcută a temei P3. Rulare: pytest -q"""
import networkx as nx
import numpy as np
import pytest

from sada.p3.ca import RuleTable, TableCA, count_structures, read_rle
from sada.p3.graph_io import path_edges, summarize
from sada.p3.metrics import connectivity_report, od_costs
from sada.p3.od import sample_od_pairs

SPREAD = """@RULE Spread
@TABLE
n_states:2
neighborhood:vonNeumann
symmetries:rotate4
var a={0,1}
var b={0,1}
var c={0,1}
0,1,a,b,c,1
"""


def test_rule_rotate4_spreads_to_all_neighbours():
    ca = TableCA(RuleTable.from_text(SPREAD))
    g = np.zeros((5, 5), dtype=np.int16)
    g[2, 2] = 1
    g = ca.step(g)
    assert g.sum() == 5 and g[1, 2] == g[3, 2] == g[2, 1] == g[2, 3] == 1


def test_compact_transitions_and_default_identity():
    rule = RuleTable.from_text("@TABLE\nn_states:3\nneighborhood:vonNeumann\nsymmetries:none\n200002\n100000\n")
    ca = TableCA(rule)
    g = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 2]], dtype=np.int16)
    g2 = ca.step(g)
    assert g2[1, 1] == 0 and g2[2, 2] == 2   # 1 izolat dispare; 2 izolat rămâne


def test_read_rle(tmp_path):
    p = tmp_path / "x.rle"
    p.write_text("#C test\nx = 3, y = 2, rule = Test\n2A.$B2C!\n")
    g = read_rle(p)
    assert g.tolist() == [[1, 1, 0], [2, 3, 3]]


def test_count_structures():
    g = np.zeros((10, 10), dtype=np.int16)
    g[1:3, 1:3] = 1
    g[6:9, 6:9] = 2
    assert count_structures(g, min_cells=4) == 2


@pytest.fixture
def grid_graph():
    G = nx.MultiDiGraph(nx.grid_2d_graph(5, 5).to_directed())
    G = nx.relabel_nodes(G, {n: f"{n[0]}_{n[1]}" for n in G.nodes})
    for u, v, k in G.edges(keys=True):
        G[u][v][k]["length"] = 100.0
    for n in G.nodes:
        G.nodes[n]["population"] = 10.0
    return G


def test_od_and_costs(grid_graph):
    pairs = sample_od_pairs(grid_graph, 30, np.random.default_rng(0))
    base = od_costs(grid_graph, pairs)
    assert np.all(np.isfinite(base)) and len(pairs) == 30
    rep = connectivity_report(base, base)
    assert rep["od_connected_pct"] == 100.0 and rep["cost_increase_pct"] == 0.0


def test_path_edges_and_summary(grid_graph):
    p = nx.shortest_path(grid_graph, "0_0", "0_3", weight="length")
    assert len(path_edges(grid_graph, p)) == 3
    assert summarize(grid_graph)["components"] == 1


def test_backup_route_is_edge_disjoint(grid_graph):
    from sada.p3.graph_io import path_edges
    from sada.p3.routes import backup_route, primary_route
    p = primary_route(grid_graph, "0_0", "4_4")
    try:
        b = backup_route(grid_graph, "0_0", "4_4", p)
    except NotImplementedError:
        pytest.skip("backup_route nu e încă implementat")
    pe = {(u, v) for u, v, _ in path_edges(grid_graph, p)}
    be = {(u, v) for u, v, _ in path_edges(grid_graph, b)}
    assert b[0] == "0_0" and b[-1] == "4_4" and not (pe & be)
