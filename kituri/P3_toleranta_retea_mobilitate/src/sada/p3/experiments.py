"""O rulare a experimentului principal, apelată de scripts/run_all.py. TODO (GHID.md, pasul 8).

Schița:
    cfg = scenario["_cfg"]
    G = load_graph(cfg["data"]["graph"]); pairs = load_pairs(cfg["data"]["od_pairs"])
    base = od_costs(G, pairs)
    edges_to_fail = ... după scenario["failure"] (random / targeted / group)
    rec = HierarchicalRecovery(...) după variant["levels"] (none / level2 / all)
    pas cu pas: elimină muchiile (toate deodată sau progresiv), rec.step(network, t)
    return {"od_connected_pct": ..., "cost_increase_pct": ...,
            "backup_routes_used": ..., "recovery_steps": ...}
"""
from __future__ import annotations


def run_one(scenario: dict, variant: dict, rng, seed: int) -> dict:
    raise NotImplementedError("sada.p3.experiments.run_one (GHID.md, pasul 8)")
