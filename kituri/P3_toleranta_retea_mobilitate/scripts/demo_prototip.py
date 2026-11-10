"""Demonstrația pentru prototipul din săptămâna 9 (milestones/M3_sapt9_prototip.md).

Aplică un defect în grup, lasă controllerul ierarhic să reacționeze câțiva
pași și arată: câte perechi a rezolvat fiecare nivel, ponderea perechilor
servite înainte și după, și o hartă cu muchiile căzute.

    python scripts/demo_prototip.py --group coridor_inundatie
    python scripts/demo_prototip.py --random 0.05          # fără fișierul de scenarii: 5% muchii aleatoare
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from sada.config import load_config
from sada.p3 import failures, routes
from sada.p3.graph_io import load_graph
from sada.p3.od import load_pairs
from sada.p3.recovery import HierarchicalRecovery, NetworkState
from sada.plotting import savefig, setup_style


def draw(state, path, title):
    G = state.G
    xs = {n: d.get("x") for n, d in G.nodes(data=True)}
    ys = {n: d.get("y") for n, d in G.nodes(data=True)}
    if any(v is None for v in xs.values()):
        return False
    setup_style()
    fig, ax = plt.subplots(figsize=(6, 6))
    for u, v in G.edges():
        ax.plot([xs[u], xs[v]], [ys[u], ys[v]], color="0.8", lw=0.4)
    shown = 0
    for od, lvl in state.level.items():
        if lvl == 2 and state.current.get(od) and shown < 15:
            r = state.current[od]
            ax.plot([xs[n] for n in r], [ys[n] for n in r], color="C2", lw=1.2, alpha=0.8)
            shown += 1
    for e in state.failed:
        u, v = e[0], e[1]
        ax.plot([xs[u], xs[v]], [ys[u], ys[v]], color="C3", lw=2)
    ax.plot([], [], color="C3", lw=2, label="muchii căzute")
    ax.plot([], [], color="C2", lw=1.2, label="rute de rezervă folosite (max. 15)")
    ax.set_aspect("equal")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title(title)
    ax.grid(False)
    savefig(fig, path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", help="numele unui scenariu din data.group_scenarios")
    ap.add_argument("--random", type=float, default=0.05)
    ap.add_argument("--steps", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    cfg = load_config("config/default.yaml")
    G = load_graph(cfg["data"]["graph"])
    pairs = load_pairs(cfg["data"]["od_pairs"])
    try:
        R = routes.precompute(G, pairs, weight=cfg["od"]["weight"])
        state = NetworkState(G, pairs, R)
        if a.group:
            scen = json.load(open(cfg["data"]["group_scenarios"], encoding="utf-8"))
            edges = failures.group_failure(G, scen[a.group] if isinstance(scen, dict) else scen)
            label = a.group
        else:
            edges = failures.random_failures(G, a.random, np.random.default_rng(a.seed))
            label = f"{a.random:.0%} muchii aleatoare"
        before = state.served_share()
        ctrl = HierarchicalRecovery(cfg, log_path="results/logs/demo_p3.jsonl")
        state.fail(edges)
        after_fail = state.served_share()
        for t in range(1, a.steps + 1):
            ctrl.step(state, t)
    except NotImplementedError as e:
        raise SystemExit("Pentru demonstrație trebuie implementate routes.precompute, failures.* și "
                         f"HierarchicalRecovery.\nLipsește: {e}")
    lv = Counter(state.level.values())
    print(f"Defect: {label}, {len(edges)} muchii căzute")
    print(f"Perechi servite: înainte {before:.1%}, imediat după defect {after_fail:.1%}, "
          f"după recuperare {state.served_share():.1%}")
    ps = state.served_share(priority_only=True)
    print("Prioritare servite după recuperare: " + ("nu există perechi prioritare" if np.isnan(ps) else f"{ps:.1%}"))
    print("Perechi pe niveluri (0 = ruta principală, 2 = rezervă, 3 = recalculată):", dict(sorted(lv.items())))
    print(f"Decizii în jurnal: {len(ctrl.k.history)} (results/logs/demo_p3.jsonl)")
    if draw(state, "results/figures/demo_p3_map", f"Defect: {label}"):
        print("Harta: results/figures/demo_p3_map.pdf")


if __name__ == "__main__":
    main()
