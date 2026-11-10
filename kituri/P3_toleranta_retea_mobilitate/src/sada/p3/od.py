"""Perechile origine-destinație (OD): eșantionare și salvare."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def sample_od_pairs(G, n_pairs: int, rng: np.random.Generator, pop_attr: str = "population",
                    priority_pairs: list[tuple] | None = None) -> pd.DataFrame:
    """Eșantionează perechi OD proporțional cu populația nodurilor (sau uniform, dacă
    nodurile n-au populație). Perechile prioritare (spital, nod de transport) se
    adaugă separat, cu priority=True."""
    nodes = list(G.nodes)
    pop = np.array([float(G.nodes[n].get(pop_attr, 0.0) or 0.0) for n in nodes])
    w = pop / pop.sum() if pop.sum() > 0 else np.full(len(nodes), 1.0 / len(nodes))
    pairs = set()
    tries = 0
    while len(pairs) < n_pairs and tries < 50 * n_pairs:
        o, d = rng.choice(len(nodes), size=2, p=w)
        if o != d:
            pairs.add((nodes[o], nodes[d]))
        tries += 1
    rows = [{"origin": o, "destination": d, "priority": False} for o, d in sorted(pairs, key=str)]
    rows += [{"origin": o, "destination": d, "priority": True} for o, d in (priority_pairs or [])]
    return pd.DataFrame(rows)


def save_pairs(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_pairs(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"origin": str, "destination": str})
