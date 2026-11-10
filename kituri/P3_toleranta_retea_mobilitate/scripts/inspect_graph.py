"""Verifică graful (GHID.md, pasul 1): număr de noduri și muchii, orientare,
conexitate, atribute, și îl desenează.

    python scripts/inspect_graph.py data/p3_retea/<graf>.graphml
"""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt

from sada.p3.graph_io import load_graph, summarize
from sada.plotting import savefig, setup_style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("graph")
    a = ap.parse_args()
    G = load_graph(a.graph)
    print(json.dumps(summarize(G), indent=1, ensure_ascii=False))
    setup_style()
    fig, ax = plt.subplots(figsize=(6, 6))
    xs = {n: d.get("x") for n, d in G.nodes(data=True)}
    ys = {n: d.get("y") for n, d in G.nodes(data=True)}
    if all(v is not None for v in xs.values()):
        for u, v in G.edges():
            ax.plot([xs[u], xs[v]], [ys[u], ys[v]], color="0.5", lw=0.4)
        ax.scatter(list(xs.values()), list(ys.values()), s=2, color="C0")
        ax.set_aspect("equal")
        ax.set_xlabel("Longitudine [°]")
        ax.set_ylabel("Latitudine [°]")
    else:
        import networkx as nx
        nx.draw(G, ax=ax, node_size=2, width=0.3, arrows=False)
    ax.set_title(f"Rețeaua: {G.number_of_nodes()} noduri, {G.number_of_edges()} muchii")
    savefig(fig, "results/figures/network")
    print("Desen: results/figures/network.pdf")


if __name__ == "__main__":
    main()
