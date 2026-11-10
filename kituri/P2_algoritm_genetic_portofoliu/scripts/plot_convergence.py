"""Figura cu adaptarea în timp: cel mai bun individ pe generații, optimul curent
și momentele schimbărilor. Rulează o singură dată algoritmul genetic, cu și
fără controller. Merge după ce ați implementat DynamicGA și controllerul.

    python scripts/plot_convergence.py data/dev/dev_A_20.json data/dev/changes_dev_A_20.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from sada.config import load_config
from sada.p2.controller import DynamicGAController
from sada.p2.dynamic import ChangeSchedule
from sada.p2.ga import DynamicGA
from sada.p2.problem import Problem
from sada.plotting import savefig, setup_style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance")
    ap.add_argument("changes")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--response", default="hypermutation")
    a = ap.parse_args()
    cfg = load_config("config/default.yaml")
    setup_style()
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for label, use_ctrl in (("fără adaptare", False), (f"MAPE-K ({a.response})", True)):
        p = Problem.from_json(a.instance)
        ga = DynamicGA(p, cfg["ga"], np.random.default_rng(a.seed))
        ctrl = DynamicGAController({**cfg["controller"], "response": a.response}) if use_ctrl else None
        h = ga.run(cfg["ga"]["generations"], ChangeSchedule.from_json(a.changes), ctrl)
        g = [r["generation"] for r in h]
        y = [r["best_objective"] if r["best_feasible"] else np.nan for r in h]
        ax.plot(g, y, label=label, lw=1.2)
    opt_file = Path("results") / f"optima_{Problem.from_json(a.instance).name}.json"
    if opt_file.exists():
        st = json.loads(opt_file.read_text(encoding="utf-8"))["states"]
        bounds = [s["from_generation"] for s in st] + [cfg["ga"]["generations"]]
        for s, g0, g1 in zip(st, bounds[:-1], bounds[1:]):
            ax.hlines(s["optimum"], g0, g1, colors="k", linestyles=":", lw=1)
        ax.plot([], [], "k:", label="optim exact")
    for c in ChangeSchedule.from_json(a.changes).changes:
        ax.axvline(c["generation"], color="grey", ls="--", lw=0.8)
    ax.set_xlabel("Generație")
    ax.set_ylabel("Valoarea celei mai bune soluții fezabile")
    ax.set_title("Revenirea după schimbările problemei (linii punctate verticale)")
    ax.legend()
    savefig(fig, "results/figures/convergence")
    print("Salvat results/figures/convergence.pdf")


if __name__ == "__main__":
    main()
