"""Varianta cu două obiective (beneficiu și echitate), cu NSGA-II din pymoo.
GHID.md, pasul 8.

Ce e gata: rularea NSGA-II și calculul hipervolumului.
Ce faceți voi: clasa problemei (TODO în _evaluate) și alegerea punctului de referință.

pymoo minimizează, deci obiectivele se dau cu minus: F = [-beneficiu, -echitate].
Constrângerea de buget se dă ca G <= 0: G = [cost_total - buget].
"""
from __future__ import annotations

import numpy as np

from .problem import Problem


def make_pymoo_problem(problem: Problem):
    from pymoo.core.problem import ElementwiseProblem

    class PortfolioProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=problem.n, n_obj=2, n_ieq_constr=1, xl=0, xu=1, vtype=bool)

        def _evaluate(self, x, out, *args, **kwargs):
            # TODO: out["F"] = [-beneficiu, -echitate]; out["G"] = [cost - buget]
            # Folosiți problem.objectives(x) și problem.total_cost(x).
            raise NotImplementedError("PortfolioProblem._evaluate (GHID.md, pasul 8)")

    return PortfolioProblem()


def run_nsga2(problem: Problem, pop_size: int = 100, n_gen: int = 200, seed: int = 0):
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.operators.crossover.pntx import TwoPointCrossover
    from pymoo.operators.mutation.bitflip import BitflipMutation
    from pymoo.operators.sampling.rnd import BinaryRandomSampling
    from pymoo.optimize import minimize

    algo = NSGA2(pop_size=pop_size, sampling=BinaryRandomSampling(), crossover=TwoPointCrossover(),
                 mutation=BitflipMutation(), eliminate_duplicates=True)
    res = minimize(make_pymoo_problem(problem), algo, ("n_gen", n_gen), seed=seed, verbose=False)
    return res          # res.X = soluțiile nedominate, res.F = obiectivele lor (cu minus)


def hypervolume(F: np.ndarray, ref_point) -> float:
    """Hipervolumul frontului F (obiective minimizate) față de un punct de referință FIX.
    Folosiți același ref_point pentru toate rulările, altfel valorile nu se pot compara."""
    from pymoo.indicators.hv import HV
    return float(HV(ref_point=np.asarray(ref_point, float))(np.asarray(F, float)))
