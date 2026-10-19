"""Calculează optimul exact pentru fiecare stare a problemei (înainte și după
fiecare schimbare). Binar: căutare exhaustivă pentru n ≤ 16, altfel MILP (exact și pentru
n = 40); întreg (ramura B): programare dinamică. Rezultatul e reperul pentru „abaterea
față de optim” și pentru timpul de revenire la 95%.

    python scripts/solve_optima.py data/dev/dev_A_20.json data/dev/changes_dev_A_20.json

Ieșire: results/optima_<instanță>.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from sada.p2.dynamic import ChangeSchedule
from sada.p2.exact import solve
from sada.p2.problem import Problem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance")
    ap.add_argument("changes", nargs="?")
    a = ap.parse_args()
    p = Problem.from_json(a.instance)
    sched = ChangeSchedule.from_json(a.changes) if a.changes else ChangeSchedule([])
    states = []
    t0 = time.perf_counter()
    x, v = solve(p)
    states.append({"from_generation": 0, "optimum": v, "x": x.tolist()})
    for c in sched.changes:
        p.apply_change(c)
        x, v = solve(p)
        states.append({"from_generation": c["generation"], "after": c, "optimum": v, "x": x.tolist()})
    # numele vine din fișierul de schimbări (changes_X.json -> optima_X.json), ca mai multe
    # scenarii pe aceeași instanță să nu se suprascrie
    stem = Path(a.changes).stem.removeprefix("changes_") if a.changes else p.name
    out = Path("results") / f"optima_{stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"instance": a.instance, "states": states}, indent=1, ensure_ascii=False), encoding="utf-8")
    for s in states:
        print(f"  de la generația {s['from_generation']:4d}: optim = {s['optimum']:.2f}")
    print(f"Scris {out} în {time.perf_counter() - t0:.1f} s")


if __name__ == "__main__":
    main()
