"""Demonstrația pentru prototipul din săptămâna 9 (milestones/M3_sapt9_prototip.md).

Rulează algoritmul genetic cu controllerul pe o instanță cu schimbări și arată:
când a avut loc fiecare schimbare, când a detectat-o controllerul și ce a făcut.

    python scripts/demo_prototip.py
    python scripts/demo_prototip.py --instance data/dev/dev_A_20.json --changes data/dev/changes_dev_A_20.json --response immigrants
"""
from __future__ import annotations

import argparse

import numpy as np

from sada.config import load_config
from sada.p2.controller import DynamicGAController
from sada.p2.dynamic import ChangeSchedule
from sada.p2.ga import DynamicGA
from sada.p2.problem import Problem
from sada.timeline import plot_timeline, read_log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default="data/dev/dev_A_20.json")
    ap.add_argument("--changes", default="data/dev/changes_dev_A_20.json")
    ap.add_argument("--response", default="hypermutation")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    cfg = load_config("config/default.yaml")
    sched = ChangeSchedule.from_json(a.changes)
    p = Problem.from_json(a.instance)
    ga = DynamicGA(p, cfg["ga"], np.random.default_rng(a.seed))
    ctrl = DynamicGAController({**cfg["controller"], "response": a.response}, log_path="results/logs/demo_p2.jsonl")
    try:
        h = ga.run(cfg["ga"]["generations"], sched, ctrl)
    except NotImplementedError as e:
        raise SystemExit(f"Pentru demonstrație trebuie implementate DynamicGA și DynamicGAController.\nLipsește: {e}")
    log = read_log("results/logs/demo_p2.jsonl")
    print("Schimbări programate la generațiile:", sched.generations)
    print(f"Decizii ale controllerului: {len(log)}")
    for _, r in log.iterrows():
        print(f"  generația {int(r['t']):4d}: {r.get('assessment')} -> {r['action']}")
    # întârzierea detecției: prima decizie după fiecare schimbare
    for g in sched.generations:
        after = log[log["t"] >= g]["t"]
        print(f"  schimbarea de la {g}: " + (f"prima reacție la {int(after.iloc[0])} (+{int(after.iloc[0]) - g})"
                                            if len(after) else "nicio reacție"))
    gens = [r["generation"] for r in h]
    best = [r["best_objective"] if r["best_feasible"] else np.nan for r in h]
    pert = [(g, g + 1, c["type"]) for g, c in zip(sched.generations, sched.changes)]
    plot_timeline(gens, best, log, "results/figures/demo_p2_timeline", ylabel="Cea mai bună soluție fezabilă",
                  xlabel="Generație", perturbations=pert, title="Schimbările problemei și reacțiile controllerului")
    print("Figura: results/figures/demo_p2_timeline.pdf (pentru comparația cu varianta statică: scripts/plot_convergence.py)")


if __name__ == "__main__":
    main()
