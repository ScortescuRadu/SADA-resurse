"""Citirea și verificarea grafului rutier (GraphML)."""
from __future__ import annotations

from pathlib import Path

import networkx as nx

NUMERIC_EDGE = ("length", "travel_time", "speed_kph", "importance")
NUMERIC_NODE = ("x", "y", "population")


def load_graph(path: str | Path) -> nx.MultiDiGraph:
    """Citește GraphML. Fișierele scrise de OSMnx se citesc cu tipurile corecte;
    altfel, atributele numerice cunoscute se convertesc în float."""
    try:
        import osmnx as ox
        G = ox.load_graphml(path)
    except Exception:
        G = nx.read_graphml(path)
        if not G.is_multigraph():
            G = nx.MultiDiGraph(G) if G.is_directed() else nx.MultiGraph(G)
    for _, _, d in G.edges(data=True):
        for k in NUMERIC_EDGE:
            if k in d:
                try:
                    d[k] = float(d[k])
                except (TypeError, ValueError):
                    pass
    for _, d in G.nodes(data=True):
        for k in NUMERIC_NODE:
            if k in d:
                try:
                    d[k] = float(d[k])
                except (TypeError, ValueError):
                    pass
    return G


def summarize(G) -> dict:
    directed = G.is_directed()
    comps = (nx.number_strongly_connected_components(G) if directed
             else nx.number_connected_components(G))
    any_edge = next(iter(G.edges(data=True)), (None, None, {}))[2]
    any_node = next(iter(G.nodes(data=True)), (None, {}))[1]
    return {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "directed": directed,
            "multigraph": G.is_multigraph(),
            "components": comps, "edge_attributes": sorted(any_edge.keys()),
            "node_attributes": sorted(any_node.keys())}


def largest_component(G):
    """Cea mai mare componentă tare conexă (graf orientat) sau conexă (neorientat)."""
    comps = nx.strongly_connected_components(G) if G.is_directed() else nx.connected_components(G)
    return G.subgraph(max(comps, key=len)).copy()


def path_edges(G, path: list, weight: str = "length") -> list[tuple]:
    """Muchiile (u, v, cheie) ale unui drum dat ca listă de noduri. Între două noduri
    pot exista mai multe muchii (multigraf); se alege cea cu ponderea cea mai mică."""
    out = []
    for u, v in zip(path[:-1], path[1:]):
        if G.is_multigraph():
            k = min(G[u][v], key=lambda kk: G[u][v][kk].get(weight, 1.0))
            out.append((u, v, k))
        else:
            out.append((u, v))
    return out


def node_key(G, n):
    """Cheia nodului n în graf. Nodurile pot fi int (OSMnx) sau str (CSV, GraphML generic);
    întoarce None dacă nodul nu există."""
    if n in G:
        return n
    for cand in (str(n), _try_int(n)):
        if cand is not None and cand in G:
            return cand
    return None


def _try_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None
