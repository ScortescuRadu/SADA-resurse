"""Referințele simple: strategia lacomă și căutarea aleatoare.

Ambele întorc (x, valoare, număr_de_evaluări). Comparați cu algoritmul genetic
la ACELAȘI număr de evaluări ale funcției obiectiv, nu la același număr de generații.
"""
from __future__ import annotations

import numpy as np

from .problem import Problem


def greedy(problem: Problem):
    """Binar: sortează după valoare/cost și adaugă cât încape în buget,
    respectând dependențele. Întreg: adaugă câte o oră-vehicul acolo unde
    câștigul marginal e cel mai mare."""
    if problem.kind == "binary":
        w = problem.w_benefit * problem.benefit + problem.w_equity * problem.equity
        order = np.argsort(-(w / np.maximum(problem.cost, 1e-12)))
        x = np.zeros(problem.n, dtype=int)
        evals = 0
        changed = True
        while changed:                      # mai multe treceri, pentru dependențe
            changed = False
            for i in order:
                if x[i] or not problem.available[i]:
                    continue
                x[i] = 1
                evals += 1
                if problem.is_feasible(x):
                    changed = True
                else:
                    x[i] = 0
        return x, problem.objective(x), evals

    lo = np.where(problem.available, problem.lower, 0)
    hi = np.where(problem.available, problem.upper, 0)
    x = lo.copy()
    evals = 0
    while x.sum() < problem.budget:
        cand = np.where(x < hi)[0]
        if len(cand) == 0:
            break
        base = problem.objective(x)
        gains = []
        for i in cand:
            x[i] += 1
            gains.append(problem.objective(x) - base)
            x[i] -= 1
            evals += 1
        x[cand[int(np.argmax(gains))]] += 1
    return x, problem.objective(x), evals


def random_search(problem: Problem, n_evals: int, rng: np.random.Generator):
    """Generează n_evals soluții aleatoare și o păstrează pe cea mai bună fezabilă.
    La binar, probabilitatea de includere e raportul buget / cost total, ca o
    parte rezonabilă din soluții să încapă în buget."""
    best_x, best_v = None, -np.inf
    if problem.kind == "binary":
        q = min(0.5, problem.budget / max(problem.cost[problem.available].sum(), 1e-12))
        for _ in range(n_evals):
            x = (rng.random(problem.n) < q).astype(int) & problem.available
            if problem.is_feasible(x):
                v = problem.objective(x)
                if v > best_v:
                    best_x, best_v = x, v
    else:
        lo = np.where(problem.available, problem.lower, 0)
        hi = np.where(problem.available, problem.upper, 0)
        for _ in range(n_evals):
            share = rng.dirichlet(np.ones(problem.n))
            x = np.clip(np.floor(lo + share * (problem.budget - lo.sum())), lo, hi).astype(int)
            if problem.is_feasible(x):
                v = problem.objective(x)
                if v > best_v:
                    best_x, best_v = x, v
    return best_x, best_v, n_evals
