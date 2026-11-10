"""Rularea unei grile de experimente: scenarii × variante × seed-uri.

Funcția voastră `run_one(scenario, variant, rng, seed)` simulează o singură
rulare și întoarce un dicționar cu metricile, de exemplu
{"travel_time_mean": 312.4, "throughput": 1840}. `run_grid` o apelează pentru
toate combinațiile și salvează un CSV cu câte un rând pe rulare.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

try:
    from tqdm import tqdm
except ImportError:  # tqdm e opțional
    def tqdm(x, **_):
        return x


def seeds_from_config(exp_cfg: dict) -> list[int]:
    base = int(exp_cfg.get("base_seed", 12345))
    n = int(exp_cfg.get("n_runs", 20))
    return [base + i for i in range(n)]


def run_grid(run_one: Callable[..., dict], scenarios: dict, variants: dict, seeds: list[int],
             out_csv: str | Path | None = None) -> pd.DataFrame:
    rows = []
    jobs = [(s, v, seed) for s in scenarios for v in variants for seed in seeds]
    for sname, vname, seed in tqdm(jobs, desc="rulări"):
        rng = np.random.default_rng(seed)
        t0 = time.perf_counter()
        metrics = run_one(scenario=scenarios[sname], variant=variants[vname], rng=rng, seed=seed)
        rows.append({"scenario": sname, "variant": vname, "seed": seed,
                     "wall_time_s": round(time.perf_counter() - t0, 3), **metrics})
    df = pd.DataFrame(rows)
    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
    return df
