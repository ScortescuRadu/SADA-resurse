"""Rutele principale și rutele de rezervă (partea „precalculată” a nivelului 2).
TODO (GHID.md, pasul 3)."""
from __future__ import annotations

import networkx as nx

from .graph_io import path_edges


def primary_route(G, o, d, weight: str = "length") -> list:
    """Drumul minim, ca listă de noduri (gata)."""
    return nx.shortest_path(G, o, d, weight=weight)


def backup_route(G, o, d, primary: list, weight: str = "length") -> list | None:
    """O rută de rezervă fără muchii comune cu `primary`, sau None dacă nu există.

    TODO: două variante, alegeți una și spuneți în raport:
      - eliminați temporar muchiile rutei principale (path_edges(G, primary)) dintr-o
        copie a grafului (sau folosiți nx.restricted_view) și căutați din nou drumul minim;
      - nx.edge_disjoint_paths(G, o, d) dă drumuri fără muchii comune, dar nu neapărat scurte.
    """
    raise NotImplementedError("backup_route (GHID.md, pasul 3)")


def precompute(G, pairs, weight: str = "length") -> dict:
    """{(o, d): {"primary": [...], "primary_edges": set(...), "backup": [...] | None,
                 "backup_edges": set(...)}}  TODO."""
    raise NotImplementedError("precompute (GHID.md, pasul 3)")


__all__ = ["primary_route", "backup_route", "precompute", "path_edges"]
