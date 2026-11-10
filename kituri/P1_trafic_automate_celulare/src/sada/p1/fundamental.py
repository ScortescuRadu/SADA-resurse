"""Diagrama fundamentală (flux în funcție de densitate). Gata de folosit
după ce ați implementat RingRoad.step.

    from sada.p1.fundamental import fundamental_diagram, to_physical
    df = fundamental_diagram(np.linspace(0.05, 0.9, 18), rule="nasch", rng=rng)
    df = to_physical(df)       # veh/km, veh/h, km/h
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .nasch import RingRoad


def fundamental_diagram(densities, length: int = 1000, warmup: int = 500, measure: int = 500,
                        rng: np.random.Generator | None = None, **road_kw) -> pd.DataFrame:
    rng = rng if rng is not None else np.random.default_rng()
    rows = []
    for rho in densities:
        road = RingRoad(length=length, density=rho, rng=rng, **road_kw)
        for _ in range(warmup):
            road.step()
        speeds = np.empty(measure)
        for i in range(measure):
            road.step()
            speeds[i] = road.mean_speed
        v = speeds.mean()
        rows.append({"density": road.density, "mean_speed": v, "flow": road.density * v})
    return pd.DataFrame(rows)


def to_physical(df: pd.DataFrame, cell_m: float = 7.5, dt_s: float = 1.0) -> pd.DataFrame:
    """Transformă din unități de celulă/pas în veh/km/bandă, veh/h/bandă și km/h."""
    out = df.copy()
    out["density_veh_km"] = df["density"] * 1000.0 / cell_m
    out["flow_veh_h"] = df["flow"] * 3600.0 / dt_s
    out["speed_km_h"] = df["mean_speed"] * cell_m / dt_s * 3.6
    return out
