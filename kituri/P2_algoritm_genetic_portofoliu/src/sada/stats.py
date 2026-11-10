"""Statistică pentru raport: medie ± abatere standard, interval de încredere, comparații.

Vedeți docs/STATISTICA.md pentru explicații.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def summarize(df: pd.DataFrame, metrics: list[str], by=("scenario", "variant")) -> pd.DataFrame:
    """Un rând pe grup, cu n, medie, abatere standard (ddof=1) și IC 95% pentru medie."""
    out = []
    for keys, g in df.groupby(list(by), sort=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        row = dict(zip(by, keys))
        for m in metrics:
            x = g[m].dropna().to_numpy(dtype=float)
            n = len(x)
            mean = x.mean() if n else np.nan
            sd = x.std(ddof=1) if n > 1 else np.nan
            half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) if n > 1 else np.nan
            row.update({f"{m}_n": n, f"{m}_mean": mean, f"{m}_std": sd,
                        f"{m}_ci_low": mean - half, f"{m}_ci_high": mean + half})
        out.append(row)
    return pd.DataFrame(out)


def fmt(mean: float, std: float, decimals: int = 1, unit: str = "", comma: bool = True) -> str:
    """'124,3 ± 8,7 s' (virgulă zecimală, ca în română)."""
    s = f"{mean:.{decimals}f} ± {std:.{decimals}f}"
    if comma:
        s = s.replace(".", ",")
    return f"{s} {unit}".strip()


def a12(x, y) -> float:
    """Vargha–Delaney A12: probabilitatea ca o valoare din x să fie mai mare decât una din y.
    0,5 = fără diferență; aprox. 0,56 / 0,64 / 0,71 = efect mic / mediu / mare."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    gt = (x[:, None] > y[None, :]).sum()
    eq = (x[:, None] == y[None, :]).sum()
    return (gt + 0.5 * eq) / (len(x) * len(y))


def compare(x, y) -> dict:
    """Test Mann–Whitney U bilateral + mărimea efectului A12."""
    res = stats.mannwhitneyu(x, y, alternative="two-sided")
    return {"U": float(res.statistic), "p_value": float(res.pvalue), "A12": float(a12(x, y))}
