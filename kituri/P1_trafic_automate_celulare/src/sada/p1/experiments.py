"""O rulare a experimentului principal. Apelată de scripts/run_all.py
pentru fiecare scenariu × variantă × seed din config/default.yaml.

TODO (GHID.md, pasul 8). Schița:

    cfg = scenario["_cfg"]
    corridor = Corridor(cfg, scenario["inflow_veh_h"], rng)
    if variant["controller"] == "adaptive":
        ctrl = TrafficController(cfg["controller"], log_path=...)
    else:
        for s in range(corridor.n_segments): corridor.set_rule(s, variant["rule"])
        ctrl = FixedController()
    for t in range(total_steps):
        incident on/off după scenario.get("incident")
        corridor.step()
        if t % window_steps == 0: ctrl.step(corridor, t)
    return {"travel_time_mean": ..., "throughput": ..., "recovery_time": ...}

Metricile se calculează doar după perioada de încălzire (model.warmup_s).
"""
from __future__ import annotations


def run_one(scenario: dict, variant: dict, rng, seed: int) -> dict:
    raise NotImplementedError("sada.p1.experiments.run_one (GHID.md, pasul 8)")
