"""Demonstrația pentru prototipul din săptămâna 9 (milestones/M3_sapt9_prototip.md).

Rulează coridorul cu controllerul adaptiv și, separat, cu regula fixă, pe același
seed, cu incidentul din scenariul `incident`. Produce:
  - results/logs/demo_p1.jsonl            jurnalul deciziilor
  - results/figures/demo_p1_timeline.pdf  viteza pe tronsonul incidentului, cu deciziile marcate

    python scripts/demo_prototip.py
    python scripts/demo_prototip.py --duration 2400 --seed 7
"""
from __future__ import annotations

import argparse

import numpy as np

from sada.config import load_config
from sada.mapek import FixedController
from sada.p1.controller import TrafficController
from sada.p1.corridor import Corridor
from sada.timeline import plot_timeline, read_log

NEEDED = "Corridor (step, segment_measurements, block, set_rule) și TrafficController"


def simulate(cfg, scen, adaptive, seed, duration_s, log_path=None):
    m = cfg["model"]
    dt = m["dt_s"]
    rng = np.random.default_rng(seed)
    cor = Corridor(cfg, scen["inflow_veh_h"], rng)
    ctrl = TrafficController(cfg["controller"], log_path=log_path) if adaptive else FixedController()
    inc = scen.get("incident")
    seg = int(inc["position_m"] // m["segment_m"]) if inc else 0
    window = int(cfg["controller"]["window_s"] / dt)
    t_s, v_seg = [], []
    for step in range(int(duration_s / dt)):
        t = step * dt
        if inc:
            active = inc["start_s"] <= t < inc["start_s"] + inc["duration_s"]
            cor.block(inc["lane"], int(inc["position_m"] / m["cell_m"]), active)
        cor.step()
        if step % window == 0 and step > 0:
            meas = cor.segment_measurements()
            t_s.append(t)
            v_seg.append(float(np.asarray(meas["speed_km_h"])[seg]))
            ctrl.step(cor, t)
    return t_s, v_seg, cor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="incident")
    ap.add_argument("--duration", type=float, default=3000)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    cfg = load_config("config/default.yaml")
    if any(cfg["controller"].get(k) is None for k in ("enter_dense", "exit_dense", "enter_jam", "exit_jam")):
        print("ATENȚIE: pragurile controllerului sunt încă null în config (controller.*). Completați-le din diagrama fundamentală.")
    scen = cfg["scenarios"][a.scenario]
    try:
        t, v_ad, cor = simulate(cfg, scen, True, a.seed, a.duration, "results/logs/demo_p1.jsonl")
        t2, v_fix, cor_fix = simulate(cfg, scen, False, a.seed, a.duration)
    except NotImplementedError as e:
        raise SystemExit(f"Pentru demonstrație trebuie implementate: {NEEDED}.\nLipsește: {e}")
    log = read_log("results/logs/demo_p1.jsonl")
    inc = scen.get("incident")
    pert = [(inc["start_s"], inc["start_s"] + inc["duration_s"], "incident")] if inc else []
    plot_timeline(t, v_ad, log, "results/figures/demo_p1_timeline", ylabel="Viteză pe tronson [km/h]",
                  xlabel="Timp simulat [s]", label="adaptiv", perturbations=pert,
                  extra_series={"regulă fixă": (t2, v_fix)},
                  title="Tronsonul incidentului: viteză și deciziile controllerului")
    print(f"Decizii ale controllerului: {len(log)}")
    for _, r in log.head(10).iterrows():
        print(f"  t = {r['t']:7.0f} s  ->  {r['action']}")
    tt = lambda c: np.mean(c.travel_times) if c.travel_times else float("nan")
    print(f"\nTimp mediu de parcurs: adaptiv {tt(cor):.1f} s, fix {tt(cor_fix):.1f} s "
          f"(o singură rulare; pentru concluzii folosiți run_all.py)")
    print("Figura: results/figures/demo_p1_timeline.pdf")


if __name__ == "__main__":
    main()
