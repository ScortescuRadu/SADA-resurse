"""Numerele pentru secțiunea de rezultate: pentru fiecare scenariu și metrică,
comparația dintre fiecare variantă adaptivă și referință (diferența procentuală
a mediilor, testul Mann–Whitney și mărimea efectului A12).

    python scripts/report_numbers.py

Referința și variantele adaptive se aleg în config, la `report`; direcția
„mai bine” a fiecărei metrici, la `figures.metrics[*].better` (lower/higher).
Rezultatul: results/tables/comparisons.md, gata de transformat în text.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sada.config import load_config
from sada.stats import compare


def main():
    cfg = load_config("config/default.yaml")
    rep = cfg.get("report", {})
    base, adaptive = rep.get("baseline"), rep.get("adaptive", [])
    if not base or not adaptive:
        raise SystemExit("Completați report.baseline și report.adaptive în config.")
    df = pd.read_csv("results/results.csv")
    lines = ["| Scenariu | Metrică | Variantă | Referință (medie) | Variantă (medie) | Diferență | p (Mann–Whitney) | A12 | Concluzie |",
             "|---|---|---|---|---|---|---|---|---|"]
    for m in cfg["figures"]["metrics"]:
        name, better = m["name"], m.get("better", "lower")
        for s in dict.fromkeys(df["scenario"]):
            b = df[(df.scenario == s) & (df.variant == base)][name].dropna()
            for v in adaptive:
                x = df[(df.scenario == s) & (df.variant == v)][name].dropna()
                if len(b) < 2 or len(x) < 2:
                    continue
                diff = 100 * (x.mean() - b.mean()) / abs(b.mean()) if b.mean() else np.nan
                if x.std() == 0 and b.std() == 0:      # ambele constante (variante deterministe)
                    same = np.isclose(x.mean(), b.mean())
                    c = {"p_value": 1.0 if same else 0.0, "A12": 0.5 if same else float(x.mean() > b.mean())}
                else:
                    c = compare(x, b)
                improved = (diff < 0) if better == "lower" else (diff > 0)
                if c["p_value"] >= 0.05:
                    verdict = "fără diferență semnificativă"
                else:
                    verdict = "mai bine" if improved else "mai rău"
                lines.append(f"| {s} | {m['label']} | {v} | {b.mean():.3g} | {x.mean():.3g} | {diff:+.1f}% | "
                             f"{c['p_value']:.3g} | {c['A12']:.2f} | {verdict} |")
    out = Path("results/tables/comparisons.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSalvat {out}. A12 > 0,5 înseamnă valori mai mari la variantă decât la referință.")


if __name__ == "__main__":
    main()
