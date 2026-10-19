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
        v = X @ w
        if problem.has_interactions:                 # − ½ xᵀ R x, cu R ponderat
            R = problem.w_benefit * problem.red_b + problem.w_equity * problem.red_e
            v = v - 0.5 * np.einsum("ij,ij->i", X @ R, X)
        vals = np.where(ok, v, -np.inf)
        i = int(np.argmax(vals))
        if vals[i] > best_val:
            best_val, best_code = float(vals[i]), int(codes[i])
    x = ((best_code >> bits) & 1).astype(int)
    return x, best_val


def solve_milp(problem: Problem) -> tuple[np.ndarray, float]:
    """Optimul exact pentru problemele binare de orice mărime (ramurile A și C), ca program
    liniar în numere întregi (scipy.optimize.milp, HiGHS): max w·x cu cost·x ≤ B, x_i = 0
    pentru intervențiile indisponibile și x_a ≤ x_b pentru dependențe. Pentru n = 40 durează
    câteva milisecunde; înlocuiește „cea mai bună soluție cunoscută” din GHID.md, pasul 7."""
    from scipy.optimize import Bounds, LinearConstraint, milp
    if problem.kind != "binary":
        raise ValueError("solve_milp e pentru problemele binare; pentru ramura B folosiți solve_integer_dp.")
    n = problem.n
    w = problem.w_benefit * problem.benefit + problem.w_equity * problem.equity
    A = [problem.cost[None, :]]
    lb, ub = [-np.inf], [problem.budget + 1e-9]
    idx = {k: i for i, k in enumerate(problem.ids)}
    for a, b in problem.requires.items():
        row = np.zeros(n)
        row[idx[a]], row[idx[b]] = 1, -1
        A.append(row[None, :])
        lb.append(-np.inf)
        ub.append(0)
    hi = problem.available.astype(float)
    pairs = []
    if problem.has_interactions:
        R = problem.w_benefit * problem.red_b + problem.w_equity * problem.red_e
        pairs = [(i, j, R[i, j]) for i in range(n) for j in range(i + 1, n) if R[i, j] > 0]
    m = len(pairs)
    # liniarizarea produselor: y_ij ≥ x_i + x_j − 1, y_ij ≥ 0 (redundanța r_ij > 0 se scade din obiectiv,
    # deci la optim y_ij = x_i · x_j exact)
    c = np.concatenate([-w, [r for _, _, r in pairs]])
    A = [np.hstack([row, np.zeros((1, m))]) for row in A]
    for k, (i, j, _) in enumerate(pairs):
        row = np.zeros(n + m)
        row[i], row[j], row[n + k] = 1, 1, -1
        A.append(row[None, :])
        lb.append(-np.inf)
        ub.append(1)
    res = milp(c, constraints=LinearConstraint(np.vstack(A), lb, ub), integrality=np.ones(n + m),
               bounds=Bounds(np.zeros(n + m), np.concatenate([hi, np.ones(m)])),
               options={"mip_rel_gap": 0.0})     # optim exact, nu cu toleranța implicită 1e-4
    x = np.round(res.x[:n]).astype(int)
    return x, float(problem.objective(x))


def solve_integer_dp(problem: Problem) -> tuple[np.ndarray, float]:
    """Optimul exact pentru ramura B (întreg, beneficiu concav separabil, Σ x ≤ buget):
    programare dinamică pe buget, O(n · B · (upper − lower))."""
    if problem.kind != "integer":
        raise ValueError("solve_integer_dp e pentru ramura B.")
    lo = np.where(problem.available, problem.lower, 0).astype(int)
    hi = np.where(problem.available, problem.upper, 0).astype(int)
    B = int(problem.budget) - int(lo.sum())
    if B < 0:
        raise ValueError("bugetul nu acoperă nici minimele liniilor")
    wq = problem.w_benefit + problem.w_equity * problem.equity

    def val(i, x):
        return wq[i] * problem.benefit[i] * (1 - np.exp(-x / problem.saturation[i]))
    best = np.full(B + 1, -np.inf)
    best[0] = 0.0
    choice = []
    for i in range(problem.n):
        extra = np.arange(0, hi[i] - lo[i] + 1)
        gain = np.array([val(i, lo[i] + e) for e in extra])
        new = np.full(B + 1, -np.inf)
        arg = np.zeros(B + 1, dtype=int)
        for e, gval in zip(extra, gain):
            if e > B:
                break
            cand = np.full(B + 1, -np.inf)
            cand[e:] = best[: B + 1 - e] + gval
            m = cand > new
            new[m], arg[m] = cand[m], e
        best = new
        choice.append(arg)
    b = int(np.argmax(best))
    x = lo.copy()
    for i in range(problem.n - 1, -1, -1):
        e = int(choice[i][b])
        x[i] += e
        b -= e
    return x, float(problem.objective(x))


def solve(problem: Problem) -> tuple[np.ndarray, float]:
    """Optimul exact, cu metoda potrivită tipului de problemă."""
    if problem.kind == "integer":
        return solve_integer_dp(problem)
    return solve_exact(problem) if problem.n <= 16 else solve_milp(problem)
