"""Calculează importanța muchiilor (edge betweenness) și o salvează în CSV
(GHID.md, pasul 4). Pentru grafuri mari folosiți --k (eșantionare).

    python scripts/compute_importance.py --k 500
"""
from __future__ import annotations

import argparse
import time

import pandas as pd

from sada.config import load_config
from sada.p3.failures import edge_importance
from sada.p3.graph_io import load_graph


def main():
    cfg = load_config("config/default.yaml")
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=500)
    ap.add_argument("--out", default="results/edge_importance.csv")
    a = ap.parse_args()
    G = load_graph(cfg["data"]["graph"])
    t0 = time.perf_counter()
    imp = edge_importance(G, k=a.k, weight=cfg["od"]["weight"])
    rows = [{"u": e[0], "v": e[1], "key": e[2] if len(e) > 2 else 0, "importance": val} for e, val in imp.items()]
    df = pd.DataFrame(rows).sort_values("importance", ascending=False)
    df.to_csv(a.out, index=False)
    print(f"{len(df)} muchii, calcul în {time.perf_counter() - t0:.1f} s -> {a.out}")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
