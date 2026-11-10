"""Demonstrația pentru prototipul din săptămâna 9 (milestones/M3_sapt9_prototip.md).

Rulează fereastra 07:00–09:00 (8 ferestre de 15 minute) cu controllerul ales,
cu o creștere a cererii pe o linie la a patra fereastră, și arată: deciziile,
bugetul de ore-vehicul (trebuie să rămână constant) și o hartă termică cu
gradul de încărcare (linii × ferestre), înainte și după controller.

    python scripts/demo_prototip.py                     # regula simplă
    python scripts/demo_prototip.py --controller ga
    python scripts/demo_prototip.py --synthetic         # fără date: un sistem inventat, pentru testarea controllerului
"""
from __future__ import annotations

import argparse
import copy

import matplotlib.pyplot as plt
import numpy as np

from sada.config import load_config
from sada.mapek import FixedController
from sada.p4.controller import GAController, SimpleRuleController
from sada.p4.system import TransitSystem
from sada.plotting import savefig, setup_style

N_WINDOWS = 8


def synthetic_system(rng):
    routes = [f"L{i}" for i in range(1, 11)]
    trips = {r: float(rng.integers(2, 5)) for r in routes}
    vh = {r: float(rng.uniform(0.6, 1.4)) for r in routes}
    cap = {r: 100.0 for r in routes}
    demand = {}
    for r in routes:
        base = rng.uniform(0.2, 1.1) * trips[r] * cap[r]
        for w in range(N_WINDOWS):
            demand[(r, w)] = base * (0.7 + 0.6 * np.exp(-0.5 * ((w - 3.5) / 1.5) ** 2))
    return TransitSystem(routes, trips, vh, cap, demand)


def run(system, ctrl, perturb_route, factor):
    lf = np.zeros((len(system.routes), N_WINDOWS))
    budget = []
    for w in range(N_WINDOWS):
        system.window = w
        if w == 3 and perturb_route:
            system.demand_factor[perturb_route] = factor
        ctrl.step(system, w)
        lf[:, w] = [system.load_factor(r) for r in system.routes]
        budget.append(system.used_vehicle_hours())
    return lf, budget


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controller", choices=["rule", "ga"], default="rule")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--factor", type=float, default=1.5)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    cfg = load_config("config/default.yaml")
    rng = np.random.default_rng(a.seed)
    try:
        sys0 = synthetic_system(rng) if a.synthetic else TransitSystem.from_files(cfg)
        cls = SimpleRuleController if a.controller == "rule" else GAController
        target = max(sys0.routes, key=lambda r: sys0.load_factor(r, 3))
        lf_fix, _ = run(copy.deepcopy(sys0), FixedController(), target, a.factor)
        ctrl = cls(cfg["controller"], log_path="results/logs/demo_p4.jsonl")
        sys1 = copy.deepcopy(sys0)
        lf_ad, budget = run(sys1, ctrl, target, a.factor)
    except NotImplementedError as e:
        raise SystemExit(f"Pentru demonstrație trebuie implementate controllerul și (fără --synthetic) "
                         f"TransitSystem.from_files.\nLipsește: {e}")
    print(f"Perturbare: cererea liniei {target} × {a.factor} de la fereastra 3 (07:45)")
    print(f"Decizii: {len(ctrl.k.history)}")
    for e in ctrl.k.history[:10]:
        print(f"  fereastra {e['t']}: {e['action']}")
    drift = max(abs(b - sys0.budget_vh) for b in budget)
    print(f"Ore-vehicul pe fereastră: buget {sys0.budget_vh:.2f}, abatere maximă {drift:.3f}"
          + ("  <- ATENȚIE: bugetul nu e respectat" if drift > 1e-6 * max(1, sys0.budget_vh) + 1e-9 else ""))
    print(f"Ponderea (linie, fereastră) peste 100%: fix {np.mean(lf_fix > 1):.1%}, controller {np.mean(lf_ad > 1):.1%}")
    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, lf, t in ((axes[0], lf_fix, "Orar fix"), (axes[1], lf_ad, f"Controller ({a.controller})")):
        im = ax.imshow(lf, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=1.5)
        ax.set_title(t)
        ax.set_xticks(range(N_WINDOWS), [f"{7 + w // 4}:{15 * (w % 4):02d}" for w in range(N_WINDOWS)], rotation=45)
        ax.grid(False)
    axes[0].set_yticks(range(len(sys0.routes)), sys0.routes)
    fig.colorbar(im, ax=axes, label="Grad de încărcare")
    fig.suptitle("Gradul de încărcare pe linii și ferestre de 15 minute")
    savefig(fig, "results/figures/demo_p4_heatmap")
    print("Figura: results/figures/demo_p4_heatmap.pdf")


if __name__ == "__main__":
    main()
