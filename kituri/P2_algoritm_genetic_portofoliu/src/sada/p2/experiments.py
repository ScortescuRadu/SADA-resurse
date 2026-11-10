"""O rulare a experimentului principal, apelată de scripts/run_all.py.

TODO (GHID.md, pasul 7). Schița:

    cfg = scenario["_cfg"]
    problem = Problem.from_json(scenario["instance"])
    schedule = ChangeSchedule.from_json(scenario["changes"]) if scenario.get("changes") else None
    optima = json.load(open(scenario["optima"]))     # din scripts/solve_optima.py

    if variant["method"] == "greedy":   ... baselines.greedy(problem)
    elif variant["method"] == "random": ... baselines.random_search(problem, n_evals, rng)
    else:
        ga = DynamicGA(problem, cfg["ga"], rng)
        ctrl = DynamicGAController({**cfg["controller"], "response": variant["response"]}) \
               if variant["response"] != "none" else None
        history = ga.run(cfg["ga"]["generations"], schedule, ctrl)

    return {"final_ratio": ...,            # cel mai bun fezabil / optimul curent
            "recovery_gen_mean": ...,      # generații până la 95% din noul optim, mediat pe schimbări
            "evaluations": ...}

Atenție: greedy și random nu „văd” schimbările în timpul rulării. Pentru ele,
rulați pe problema finală (după toate schimbările) sau pe fiecare stare a
problemei; spuneți în raport cum ați procedat.
"""
from __future__ import annotations


def run_one(scenario: dict, variant: dict, rng, seed: int) -> dict:
    raise NotImplementedError("sada.p2.experiments.run_one (GHID.md, pasul 7)")


def recovery_generations(history: list[dict], change_gens: list[int], optimum_after: list[float],
                         threshold: float = 0.95) -> list[float]:
    """Pentru fiecare schimbare: câte generații trec până când cel mai bun individ
    FEZABIL ajunge la `threshold` din noul optim (nan dacă nu ajunge înainte de
    schimbarea următoare). Gata de folosit."""
    import math
    out = []
    bounds = list(change_gens[1:]) + [math.inf]
    for g0, g_end, opt in zip(change_gens, bounds, optimum_after):
        rec = math.nan
        for h in history:
            if g0 <= h["generation"] < g_end and h["best_feasible"] and h["best_objective"] >= threshold * opt:
                rec = h["generation"] - g0
                break
        out.append(rec)
    return out
