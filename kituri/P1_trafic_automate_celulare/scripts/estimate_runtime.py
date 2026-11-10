"""Estimează cât durează experimentul complet, rulând o singură dată fiecare
combinație scenariu × variantă. Folosiți-l înainte de săptămâna 12, ca să
știți dacă vă ajunge o noapte sau vă trebuie mai puține rulări sau un model
mai rapid.

    python scripts/estimate_runtime.py
"""
from __future__ import annotations

import importlib
import time

from sada.config import load_config
from sada.experiment import seeds_from_config


def main():
    cfg = load_config("config/default.yaml")
    exp = cfg["experiment"]
    mod, fn = exp["runner"].split(":")
    run_one = getattr(importlib.import_module(mod), fn)
    import numpy as np
    n_runs = len(seeds_from_config(exp))
    total = 0.0
    print(f"{'scenariu':22s} {'variantă':16s} {'o rulare [s]':>12s} {'× ' + str(n_runs) + ' rulări [min]':>18s}")
    for s, scfg in cfg.get("scenarios", {}).items():
        for v, vcfg in cfg.get("variants", {}).items():
            t0 = time.perf_counter()
            try:
                run_one(scenario={**(scfg or {}), "_cfg": cfg}, variant=vcfg,
                        rng=np.random.default_rng(exp.get("base_seed", 0)), seed=exp.get("base_seed", 0))
            except NotImplementedError as e:
                raise SystemExit(f"Încă nu e implementat: {e}")
            dt = time.perf_counter() - t0
            total += dt * n_runs
            print(f"{s:22s} {v:16s} {dt:12.2f} {dt * n_runs / 60:18.1f}")
    print(f"\nTotal estimat: {total / 60:.1f} minute ({total / 3600:.1f} ore), pe un singur nucleu.")
    if total > 6 * 3600:
        print("Peste 6 ore: reduceți durata simulării, numărul de scenarii sau optimizați partea cea mai lentă "
              "(profilați cu: python -m cProfile -s cumtime scripts/run_all.py --set experiment.n_runs=1).")


if __name__ == "__main__":
    main()
