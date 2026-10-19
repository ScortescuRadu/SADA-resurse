"""Comparații pereche pe seed, cu corecție pentru teste multiple. Se pune în src/sada/ lângă
stats.py (din kit) și merge cu results.csv produs de scripts/run_all.py.

    from sada.statistica_pereche import paired_table
    t = paired_table(df, scenarios=["incident"], comparisons=[("adaptiv", "fix_nasch")],
                     metrics=["travel_time_mean", "recovery_time"])
    t.to_csv("results/tables/comparisons_paired.csv", index=False)

De ce pereche: dacă toate variantele primesc același seed, ele văd aceeași cerere, aceleași
defecte sau aceeași populație inițială. Diferența pe același seed are mult mai puțin zgomot decât
diferența dintre două grupuri independente, deci Wilcoxon cu semn pe diferențe e testul potrivit,
nu Mann–Whitney (care e în kit, în report_numbers.py). Verificați întâi că run_one chiar folosește
seed-ul la fel în toate variantele.

De ce Holm: cu 3 scenarii × 4 comparații × 5 metrici faceți 60 de teste. La p < 0,05, cam 3 ies
„semnificative” din întâmplare. Holm corectează asta și e mai puțin conservator decât Bonferroni.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def holm(pvals) -> np.ndarray:
    """p-valorile corectate Holm (aceeași ordine ca la intrare)."""
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - k) * p[i]))
        adj[i] = running
    return adj


def bootstrap_ci(d, n_boot: int = 4000, level: float = 0.95, seed: int = 0) -> tuple[float, float]:
    """Intervalul de încredere bootstrap (percentile) pentru media diferențelor d."""
    d = np.asarray(d, float)
    means = np.random.default_rng(seed).choice(d, size=(n_boot, len(d)), replace=True).mean(axis=1)
    a = (1 - level) / 2 * 100
    return float(np.percentile(means, a)), float(np.percentile(means, 100 - a))


def a12(x, y) -> float:
    """Vargha–Delaney A12: probabilitatea ca o valoare din x să fie mai mare decât una din y."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(((x[:, None] > y[None, :]).sum() + 0.5 * (x[:, None] == y[None, :]).sum()) / (len(x) * len(y)))


def paired_table(df: pd.DataFrame, scenarios, comparisons, metrics, seed_col: str = "seed") -> pd.DataFrame:
    """Un rând pe (scenariu, comparație A − B, metrică), cu media lui A și B, diferența medie,
    IC 95% bootstrap, p Wilcoxon, p corectat Holm (pe tot tabelul) și A12.

    Dacă ambele variante sunt deterministe (aceeași valoare la toate seed-urile), nu se face test:
    diferența e exactă și p rămâne NaN. Nu raportați p pentru 20 de copii ale aceleiași rulări."""
    rows = []
    for s in scenarios:
        for a, b in comparisons:
            for m in metrics:
                A = df[(df.scenario == s) & (df.variant == a)].set_index(seed_col)[m]
                B = df[(df.scenario == s) & (df.variant == b)].set_index(seed_col)[m]
                d = (A - B).dropna()
                if d.empty:
                    continue
                deterministic = A.std() < 1e-12 and B.std() < 1e-12
                if deterministic:
                    p, lo, hi = np.nan, d.mean(), d.mean()
                else:
                    p = stats.wilcoxon(d, zero_method="zsplit").pvalue if np.any(np.abs(d) > 1e-12) else 1.0
                    lo, hi = bootstrap_ci(d.to_numpy())
                rows.append({"scenario": s, "comparison": f"{a} − {b}", "metric": m, "mean_A": A.mean(),
                             "mean_B": B.mean(), "diff": d.mean(), "ci_low": lo, "ci_high": hi, "p": p,
                             "A12": a12(A.dropna(), B.dropna()), "n": len(d), "deterministic": deterministic})
    t = pd.DataFrame(rows)
    mask = t["p"].notna()
    t.loc[mask, "p_holm"] = holm(t.loc[mask, "p"])
    return t


def to_markdown(t: pd.DataFrame, decimals: int = 3) -> str:
    """Tabelul de mai sus, gata de pus în raport (virgulă zecimală)."""
    def f(x):
        return "–" if pd.isna(x) else f"{x:.{decimals}f}".replace(".", ",")
    lines = ["| Scenariu | Comparație | Metrică | A | B | A − B [IC 95%] | p (Holm) | A12 |",
             "|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        ci = "exact" if r.deterministic else f"[{f(r.ci_low)}; {f(r.ci_high)}]"
        p = "–" if pd.isna(r.p) else f"{r.p_holm:.2g}"
        lines.append(f"| {r.scenario} | {r.comparison} | {r.metric} | {f(r.mean_A)} | {f(r.mean_B)} | "
                     f"{f(r.diff)} {ci} | {p} | {r.A12:.2f} |")
    return "\n".join(lines) + "\n"
