"""Metrici pe perechile OD: conectivitate și costul de parcurs.

Calculul grupează perechile după origine și face un singur Dijkstra pe origine,
ceea ce e mult mai rapid decât câte un drum minim pe pereche.
"""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd


def od_costs(G, pairs: pd.DataFrame, weight: str = "length") -> np.ndarray:
    """Costul drumului minim pentru fiecare pereche (inf dacă nu există drum)."""
    nodes = set(G.nodes)
    cost = np.full(len(pairs), np.inf)
    for o, idx in pairs.groupby("origin").groups.items():
        o_key = _match(o, nodes)
        if o_key is None:
            continue
        dist = nx.single_source_dijkstra_path_length(G, o_key, weight=weight)
        for i in idx:
            d_key = _match(pairs.at[i, "destination"], nodes)
            cost[pairs.index.get_loc(i)] = dist.get(d_key, np.inf)
    return cost


def _match(n, nodes):
    """Nodurile pot fi int (OSMnx) sau str (GraphML citit generic, CSV)."""
    if n in nodes:
        return n
    for cand in (str(n), _try_int(n)):
        if cand in nodes:
            return cand
    return None


def _try_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def connectivity_report(cost_now: np.ndarray, cost_base: np.ndarray, priority=None) -> dict:
    """Procentul de perechi conectate și creșterea medie a costului (doar pe cele conectate)."""
    conn = np.isfinite(cost_now)
    out = {"od_connected_pct": 100.0 * conn.mean(),
           "cost_increase_pct": 100.0 * float(np.mean(cost_now[conn] / cost_base[conn] - 1.0)) if conn.any() else np.nan}
    if priority is not None and np.any(priority):
        out["priority_connected_pct"] = 100.0 * conn[np.asarray(priority)].mean()
    return out
