"""Diagrama spațiu-timp pentru inel (GHID.md, pasul 2). Merge după ce ați implementat RingRoad.step.

    python scripts/space_time.py --density 0.4 --p 0.3 --rule nasch
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from sada.p1.nasch import RingRoad
from sada.plotting import savefig, setup_style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=400)
    ap.add_argument("--density", type=float, default=0.3)
    ap.add_argument("--p", type=float, default=0.3)
    ap.add_argument("--p0", type=float, default=0.6)
    ap.add_argument("--vmax", type=int, default=2)
    ap.add_argument("--rule", default="nasch")
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    road = RingRoad(a.length, a.density, a.vmax, a.p, a.p0, a.rule, np.random.default_rng(a.seed))
    for _ in range(200):           # încălzire
        road.step()
    rows = []
    for _ in range(a.steps):
        road.step()
        rows.append(road.occupancy())
    img = np.ma.masked_less(np.array(rows), 0)       # celulele goale rămân albe
    setup_style()
    fig, ax = plt.subplots(figsize=(6.5, 5))
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("white")
    im = ax.imshow(img, cmap=cmap, vmin=0, vmax=a.vmax, aspect="auto", interpolation="nearest")
    fig.colorbar(im, ax=ax, label="Viteză [celule/pas]", ticks=range(a.vmax + 1))
    ax.set_xlabel("Poziție [celule de 7,5 m]")
    ax.set_ylabel("Timp [pași de 1 s]")
    ax.set_title(f"Diagrama spațiu-timp, {a.rule}, ρ = {a.density}, p = {a.p}")
    ax.grid(False)
    savefig(fig, f"results/figures/space_time_{a.rule}_rho{a.density}")
    print("Salvat în results/figures/. Vehiculele oprite (culoarea închisă) formează dungi\n"
          "care coboară spre stânga: ambuteiajul se deplasează înapoi, contra sensului de mers.")


if __name__ == "__main__":
    main()
