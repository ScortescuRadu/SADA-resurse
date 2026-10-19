"""Frontul Pareto EXACT (beneficiu, echitate), ca reper pentru NSGA-II (GHID.md, pasul 8).

    from sada.p2.front_exact import exact_front, eps_front
    F = exact_front(problem)        # n ≤ 24: enumerare
    F = eps_front(problem)          # orice n: ε-constrângere iterativă cu MILP

Hipervolumul NSGA-II spune ceva doar comparat cu ceva. Raportul HV(NSGA-II) / HV(front exact)
e mult mai ușor de interpretat decât un HV absolut.

Atenție la eps_front: varianta cu o grilă fixă de ε (de exemplu 80 de valori între 0 și
echitatea maximă) poate sări puncte nedominate și umflă raportul. Aici ε urcă la fiecare pas
imediat peste echitatea punctului găsit, deci frontul e complet.
"""
from __future__ import annotations

import numpy as np

from .problem import Problem


def exact_front(problem: Problem, chunk_bits: int = 16) -> np.ndarray:
    """Frontul Pareto EXACT (beneficiu, echitate) al unei probleme binare cu n ≤ 24, prin
    enumerarea tuturor soluțiilor fezabile. Întoarce punctele nedominate, sortate după beneficiu.
    Servește ca reper pentru hipervolumul obținut de NSGA-II."""
    n = problem.n
    if n > 24:
        raise ValueError("frontul exact doar pentru n ≤ 24")
    bits = np.arange(n)
    idx = {k: i for i, k in enumerate(problem.ids)}
    req = [(idx[a], idx[b]) for a, b in problem.requires.items()]
    pts = []
    for start in range(0, 1 << n, 1 << min(chunk_bits, n)):
        codes = np.arange(start, min(start + (1 << min(chunk_bits, n)), 1 << n), dtype=np.int64)
        X = ((codes[:, None] >> bits) & 1).astype(np.int8)
        ok = (X @ problem.cost <= problem.budget + 1e-9) & ~(X[:, ~problem.available].any(axis=1))
        for a, b in req:
            ok &= ~((X[:, a] == 1) & (X[:, b] == 0))
        Xo = X[ok].astype(float)
        bb, ee = Xo @ problem.benefit, Xo @ problem.equity
        if problem.has_interactions:
            bb = bb - 0.5 * np.einsum("ij,ij->i", Xo @ problem.red_b, Xo)
            ee = ee - 0.5 * np.einsum("ij,ij->i", Xo @ problem.red_e, Xo)
        P = np.column_stack([bb, ee])
        pts.append(_nondominated(P))
    return _nondominated(np.vstack(pts))


def _nondominated(P: np.ndarray) -> np.ndarray:
    """Punctele nedominate (maximizare pe ambele coloane)."""
    if not len(P):
        return P
    P = P[np.lexsort((-P[:, 1], -P[:, 0]))]          # beneficiu descrescător, apoi echitate
    keep, best_e = [], -np.inf
    for b, e in P:
        if e > best_e + 1e-9:
            keep.append((b, e))
            best_e = e
    return np.array(keep)[::-1]


def eps_front(problem: Problem, n_eps: int = 80) -> np.ndarray:
    """Frontul exact prin ε-constrângere: max beneficiu cu echitate ≥ ε (MILP cu liniarizarea
    redundanțelor). ε parcurge [0, echitatea maximă]."""
    from scipy.optimize import Bounds, LinearConstraint, milp
    n = problem.n
    R_b = problem.red_b if problem.has_interactions else np.zeros((n, n))
    R_e = problem.red_e if problem.has_interactions else np.zeros((n, n))
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if R_b[i, j] > 0 or R_e[i, j] > 0]
    m = len(pairs)

    def solve_max(cb, ce, eps=None):
        # obiectiv: max cb·(b x − Σ rb y) + ce·(e x − Σ re y)
        c = -np.concatenate([cb * problem.benefit + ce * problem.equity,
                             [-(cb * R_b[i, j] + ce * R_e[i, j]) for i, j in pairs]])
        A, lb, ub = [np.concatenate([problem.cost, np.zeros(m)])[None]], [-np.inf], [problem.budget + 1e-9]
        for k, (i, j) in enumerate(pairs):
            row = np.zeros(n + m)
            row[i], row[j], row[n + k] = 1, 1, -1
            A.append(row[None])
            lb.append(-np.inf)
            ub.append(1)
        if eps is not None:
            A.append(np.concatenate([problem.equity, [-R_e[i, j] for i, j in pairs]])[None])
            lb.append(eps)
            ub.append(np.inf)
        res = milp(c, constraints=LinearConstraint(np.vstack(A), lb, ub), integrality=np.ones(n + m),
                   bounds=Bounds(np.zeros(n + m), np.concatenate([problem.available.astype(float), np.ones(m)])),
                   options={"mip_rel_gap": 0.0})
        if not res.success:
            return None
        return np.round(res.x[:n]).astype(int)
    # ε-constrângere iterativă (completă): după fiecare punct găsit, ε urcă imediat peste echitatea
    # lui, deci următorul punct nedominat nu poate fi sărit (o grilă fixă de ε poate sări puncte)
    pts, eps = [], 0.0
    for _ in range(n_eps * 5):
        x = solve_max(1.0, 1e-4, eps)
        if x is None:
            break
        b, e = problem.objectives(x)
        pts.append((b, e))
        eps = e + 1e-3
    return _nondominated(np.array(pts))
