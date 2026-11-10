"""Diagrama fundamentală pentru cele trei reguli, pe inel (GHID.md, pașii 3–4).

    python scripts/fundamental_diagram.py
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from sada.config import load_config
from sada.p1.fundamental import fundamental_diagram, to_physical
from sada.plotting import savefig, setup_style


def main():
    cfg = load_config("config/default.yaml")
    m = cfg["model"]
    rng = np.random.default_rng(cfg["experiment"]["base_seed"])
    dens = np.linspace(0.04, 0.9, 22)
    setup_style()
    fig, ax = plt.subplots()
    for rule in ("nasch", "vdr", "sts"):
        df = to_physical(fundamental_diagram(dens, rule=rule, vmax=m["vmax"], p=m["p"], p0=m["p0"], rng=rng),
                         m["cell_m"], m["dt_s"])
        df.to_csv(f"results/fd_{rule}.csv", index=False)
        ax.plot(df["density_veh_km"], df["flow_veh_h"], "o-", ms=3, label=rule)
    ax.set_xlabel("Densitate [veh/km/bandă]")
    ax.set_ylabel("Flux [veh/h/bandă]")
    ax.set_title("Diagrama fundamentală pe inel, trei reguli")
    ax.legend()
    savefig(fig, "results/figures/fundamental_diagram")
    print("Salvat results/figures/fundamental_diagram.pdf și results/fd_*.csv")


if __name__ == "__main__":
    main()
