"""O rulare a experimentului principal, apelată de scripts/run_all.py. TODO (GHID.md, pasul 8).

Schița:
    cfg = scenario["_cfg"]
    s0 = pd.read_csv(cfg["data"]["s0"])           # din scripts/baseline_s0.py
    loads = pd.read_csv(cfg["data"]["loads"])      # încărcările din pachet
    system = starea: curse pe linie, capacități, încărcări pe ferestre de 15 min
    perturbări după scenario: line_closure, demand_increase
    ctrl = după variant["controller"]: fixed (S0) / rule / ga
    pentru fiecare fereastră de 15 min între 07:00 și 09:00: aplică perturbările active,
        ctrl.step(system, t), calculează metricile ferestrei
    return {"overcrowded_trip_pct": ..., "mean_wait_min": ...,
            "vehicle_hours": ..., "coverage_pct": ...}
"""
from __future__ import annotations


def run_one(scenario: dict, variant: dict, rng, seed: int) -> dict:
    raise NotImplementedError("sada.p4.experiments.run_one (GHID.md, pasul 8)")
