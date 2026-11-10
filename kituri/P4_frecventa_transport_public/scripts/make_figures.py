"""Generează figurile și tabelele din raport pornind de la results/results.csv.

    python scripts/make_figures.py

Metricile de desenat se aleg în config, la figures.metrics. Pentru fiecare
metrică se produce un boxplot (results/figures/) și un tabel cu
medie ± abatere standard, în Markdown și LaTeX (results/tables/).
Figurile specifice temei (diagrama fundamentală, frontul Pareto etc.) le
adăugați voi la finalul fișierului.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sada.config import load_config
from sada.plotting import savefig, setup_style
from sada.stats import fmt, summarize


def boxplot_metric(df, metric, label, path):
    scen = list(dict.fromkeys(df["scenario"]))
    var = list(dict.fromkeys(df["variant"]))
    fig, ax = plt.subplots(figsize=(max(4.5, 1.6 * len(scen) * len(var) / 2), 3.4))
    width = 0.8 / len(var)
    for j, v in enumerate(var):
        data = [df[(df.scenario == s) & (df.variant == v)][metric].dropna() for s in scen]
        pos = np.arange(len(scen)) + (j - (len(var) - 1) / 2) * width
        bp = ax.boxplot(data, positions=pos, widths=width * 0.9, patch_artist=True, manage_ticks=False)
        for patch in bp["boxes"]:
            patch.set_facecolor(f"C{j}")
            patch.set_alpha(0.6)
        ax.plot([], [], color=f"C{j}", lw=6, alpha=0.6, label=v)
    ax.set_xticks(range(len(scen)), scen)
    ax.set_ylabel(label)
    ax.set_xlabel("Scenariu")
    ax.set_title(f"{label} pe scenarii și variante (n = rulări / grup)")
    ax.legend(title="Variantă")
    savefig(fig, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--results", default="results/results.csv")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    df = pd.read_csv(args.results)
    metrics = cfg.get("figures", {}).get("metrics", [])
    if not metrics:
        raise SystemExit("Adăugați metricile în config, la figures.metrics.")
    setup_style()
    out = Path(args.results).parent

    names = [m["name"] for m in metrics]
    summ = summarize(df, names)
    lines_md = ["| Scenariu | Variantă | " + " | ".join(f"{m['label']} [{m.get('unit', '')}]" for m in metrics) + " |",
                "|---|---|" + "---|" * len(metrics)]
    lines_tex = []
    for _, r in summ.iterrows():
        cells = [fmt(r[f"{m['name']}_mean"], r[f"{m['name']}_std"], m.get("decimals", 1)) for m in metrics]
        lines_md.append(f"| {r['scenario']} | {r['variant']} | " + " | ".join(cells) + " |")
        lines_tex.append(f"{r['scenario']} & {r['variant']} & " + " & ".join(c.replace('±', r'$\pm$') for c in cells) + r" \\")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "tables" / "summary.md").write_text("\n".join(lines_md) + "\n", encoding="utf-8")
    (out / "tables" / "summary.tex").write_text("\n".join(lines_tex) + "\n", encoding="utf-8")
    summ.to_csv(out / "tables" / "summary_full.csv", index=False)

    for m in metrics:
        label = f"{m['label']} [{m['unit']}]" if m.get("unit") else m["label"]
        boxplot_metric(df, m["name"], label, out / "figures" / f"box_{m['name']}")
    print("\n".join(lines_md))
    print(f"\nFiguri în {out / 'figures'}, tabele în {out / 'tables'}")


if __name__ == "__main__":
    main()
