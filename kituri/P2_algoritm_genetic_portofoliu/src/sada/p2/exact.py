"""Optimul exact prin căutare exhaustivă, pentru problemele binare cu n ≤ 24.

Pentru n = 20 sunt 2^20 ≈ 1,05 milioane de combinații; vectorizat cu NumPy
durează câteva secunde. Rezultatul e reperul pentru algoritmul genetic.
"""
from __future__ import annotations

import numpy as np

from .problem import Problem


def solve_exact(problem: Problem, chunk_bits: int = 16) -> tuple[np.ndarray, float]:
    if problem.kind != "binary":
        raise ValueError("Căutarea exhaustivă e doar pentru problemele binare.")
    n = problem.n
    if n > 24:
        raise ValueError(f"n = {n} e prea mare pentru căutarea exhaustivă (maxim 24).")
    bits = np.arange(n)
    idx = {k: i for i, k in enumerate(problem.ids)}
    req = [(idx[a], idx[b]) for a, b in problem.requires.items()]
    w = problem.w_benefit * problem.benefit + problem.w_equity * problem.equity
    best_val, best_code = -np.inf, None
    step = 1 << min(chunk_bits, n)
    for start in range(0, 1 << n, step):
        codes = np.arange(start, min(start + step, 1 << n), dtype=np.int64)
        X = ((codes[:, None] >> bits) & 1).astype(np.int8)
        ok = (X @ problem.cost <= problem.budget + 1e-9)
        ok &= ~(X[:, ~problem.available].any(axis=1))
        for a, b in req:
            ok &= ~((X[:, a] == 1) & (X[:, b] == 0))
        if not ok.any():
            continue
        vals = np.where(ok, X @ w, -np.inf)
        i = int(np.argmax(vals))
        if vals[i] > best_val:
            best_val, best_code = float(vals[i]), int(codes[i])
    x = ((best_code >> bits) & 1).astype(int)
    return x, best_val
