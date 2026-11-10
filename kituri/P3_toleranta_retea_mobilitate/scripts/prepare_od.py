"""Eșantionează perechile OD și le salvează (GHID.md, pasul 2). Lista se fixează
cu seed-ul din config și se refolosește în toate experimentele.

    python scripts/prepare_od.py
    python scripts/prepare_od.py --n 300 --priority data/p3_retea/prioritare.csv

Fișierul de perechi prioritare (opțional) are coloanele origin,destination.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from sada.config import load_config
from sada.p3.graph_io import load_graph
from sada.p3.metrics import od_costs
from sada.p3.od import sample_od_pairs, save_pairs


def main():
    cfg = load_config("config/default.yaml")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=cfg["od"]["n_pairs"])
    ap.add_argument("--priority", default=cfg["od"].get("priority_file"))
    a = ap.parse_args()
    G = load_graph(cfg["data"]["graph"])
    prio = None
    if a.priority:
        p = pd.read_csv(a.priority, dtype=str)
        prio = list(zip(p["origin"], p["destination"]))
    rng = np.random.default_rng(cfg["od"]["seed"])
    pairs = sample_od_pairs(G, a.n, rng, pop_attr=cfg["od"]["population_attr"], priority_pairs=prio)
    pairs["base_cost"] = od_costs(G, pairs, weight=cfg["od"]["weight"])
    save_pairs(pairs, cfg["data"]["od_pairs"])
    print(f"{len(pairs)} perechi ({int(pairs.priority.sum())} prioritare) -> {cfg['data']['od_pairs']}")
    print(f"Perechi fără drum în graful intact: {int(np.isinf(pairs.base_cost).sum())} (ar trebui să fie 0)")


if __name__ == "__main__":
    main()
