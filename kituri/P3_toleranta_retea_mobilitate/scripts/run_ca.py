"""Rulează bucla Langton (sau Byl) și salvează câteva instantanee (GHID.md, pasul 7).

Regula și modelul inițial le luați din Golly (vedeți DATE.md):
    python scripts/run_ca.py --rule data/ca/Langtons-Loops.rule --pattern data/ca/Langtons-Loops.rle \
                             --size 128 --steps 1200 --every 300
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from sada.p3.ca import RuleTable, TableCA, count_structures, read_rle
from sada.plotting import savefig, setup_style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", required=True)
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--size", type=int, default=128)
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--every", type=int, default=300)
    ap.add_argument("--min-cells", type=int, default=20)
    a = ap.parse_args()

    rule = RuleTable.from_file(a.rule)
    print(f"Regula {rule.name}: {rule.n_states} stări, {len(rule.transitions)} tranziții după simetrii")
    ca = TableCA(rule)
    grid = ca.place(read_rle(a.pattern), shape=(a.size, a.size))
    snaps = [(0, grid.copy())]
    for t in range(1, a.steps + 1):
        grid = ca.step(grid)
        if t % a.every == 0:
            snaps.append((t, grid.copy()))
            print(f"  t = {t:5d}: {count_structures(grid, a.min_cells)} structuri, {int((grid > 0).sum())} celule nenule")
    setup_style()
    fig, axes = plt.subplots(1, len(snaps), figsize=(2.6 * len(snaps), 2.8))
    for ax, (t, g) in zip(np.atleast_1d(axes), snaps):
        ax.imshow(np.ma.masked_equal(g, 0), cmap="tab10", vmin=0, vmax=9, interpolation="nearest")
        ax.set_title(f"t = {t}")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    fig.suptitle(f"{rule.name}: evoluție pe o grilă {a.size}×{a.size}")
    savefig(fig, "results/figures/ca_snapshots")
    print("Salvat results/figures/ca_snapshots.pdf")


if __name__ == "__main__":
    main()
