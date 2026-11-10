"""Figura „adaptarea în timp”: o măsurătoare din jurnalul controllerului, cu
momentele deciziilor și ale perturbărilor marcate. Este figura cea mai
importantă la demonstrație (prototipul din săptămâna 9 și prezentarea finală).

    from sada.timeline import read_log, plot_timeline
    log = read_log("results/logs/demo.jsonl")
    plot_timeline(series_t, series_y, log, "results/figures/timeline", ylabel="Viteză [km/h]",
                  perturbations=[(1200, 1320, "incident")])
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .plotting import savefig, setup_style


def read_log(path: str | Path) -> pd.DataFrame:
    """Jurnalul JSONL scris de Controller.log, ca tabel (o linie pe decizie)."""
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    return pd.DataFrame(rows)


def plot_timeline(t, y, log: pd.DataFrame | None, path, ylabel: str, xlabel: str = "Timp",
                  label: str | None = None, perturbations=(), title: str | None = None,
                  extra_series: dict | None = None, action_text=None):
    """t, y: seria de desenat. log: jurnalul (coloanele t și action).
    perturbations: listă de (început, sfârșit, etichetă), desenate ca benzi gri.
    extra_series: {"etichetă": (t, y)} pentru comparația cu varianta fixă.
    action_text: funcție action -> text scurt pentru adnotări (implicit str)."""
    setup_style()
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for t0, t1, lab in perturbations:
        ax.axvspan(t0, t1, color="0.85", zorder=0)
        ax.text(t0, 1.0, f" {lab}", transform=ax.get_xaxis_transform(), va="top", fontsize=8, color="0.3")
    ax.plot(t, y, lw=1.4, label=label or "adaptiv", color="C0")
    for name, (tt, yy) in (extra_series or {}).items():
        ax.plot(tt, yy, lw=1.2, ls="--", label=name)
    if log is not None and len(log) and "action" in log:
        dec = log[log["action"].notna()]
        for i, (_, r) in enumerate(dec.iterrows()):
            ax.axvline(r["t"], color="C3", lw=0.8, alpha=0.7)
            if i < 12:   # nu aglomerăm figura
                txt = action_text(r["action"]) if action_text else str(r["action"])
                ax.text(r["t"], 0.02 + 0.08 * (i % 3), f" {txt[:28]}", transform=ax.get_xaxis_transform(),
                        fontsize=7, color="C3", rotation=0)
        ax.plot([], [], color="C3", lw=0.8, label="decizie a controllerului")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="best", fontsize=8)
    savefig(fig, path)
    return fig
