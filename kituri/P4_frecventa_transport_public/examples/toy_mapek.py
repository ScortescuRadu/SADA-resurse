"""Exemplu complet de buclă MAPE-K, pe un sistem de jucărie.

Sistemul: o coadă de cereri servită de un număr variabil de servere.
La pasul 300 cererea crește brusc (perturbarea). Comparăm:
  - "fix":      3 servere tot timpul (referința, fără adaptare);
  - "adaptiv":  un controller MAPE-K care adaugă sau scoate servere.

Nu are legătură directă cu temele voastre. Rostul lui e să vedeți, într-un
fișier scurt care rulează, toate piesele pe care le veți avea și voi:
sistem, controller, perturbare, rulări repetate, tabel cu medie ± abatere, figură.

Rulare (din rădăcina proiectului):
    python examples/toy_mapek.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from sada.experiment import run_grid
from sada.mapek import Controller, FixedController
from sada.plotting import savefig, setup_style
from sada.stats import fmt, summarize

STEPS = 600
PERTURB_AT = 300
OUT = Path("results/toy")


# ---------------------------------------------------------------- sistemul
class QueueSystem:
    def __init__(self, rng, servers=3, lam_before=2.5, lam_after=4.5):
        self.rng = rng
        self.servers = servers
        self.queue = 0
        self.lam_before, self.lam_after = lam_before, lam_after
        self.recent_queue = []          # fereastra de măsurare
        self.recent_busy = []

    def step(self, t):
        lam = self.lam_before if t < PERTURB_AT else self.lam_after
        self.queue += self.rng.poisson(lam)
        served = min(self.queue, self.servers)
        self.queue -= served
        self.recent_queue.append(self.queue)
        self.recent_busy.append(served / self.servers)


# ---------------------------------------------------------------- controllerul
class QueueController(Controller):
    """M: coada medie și utilizarea pe fereastră. A: supraîncărcat / subutilizat / ok.
    P: +1 sau -1 server, în limite. E: schimbă numărul de servere. K: jurnal + limite."""

    def monitor(self, system, t):
        m = {"queue": float(np.mean(system.recent_queue)),
             "util": float(np.mean(system.recent_busy)),
             "servers": system.servers}
        system.recent_queue.clear()
        system.recent_busy.clear()
        return m

    def analyze(self, m, t):
        c = self.k.config
        # praguri diferite la urcare și coborâre (histerezis): evită oscilațiile
        if m["queue"] > c["queue_high"]:
            return "supraincarcat"
        if m["util"] < c["util_low"] and m["queue"] < c["queue_low"]:
            return "subutilizat"
        return "ok"

    def plan(self, state, t):
        c = self.k.config
        s = self.k.state.setdefault("servers", c["start_servers"])
        if state == "supraincarcat" and s < c["max_servers"]:
            return +1
        if state == "subutilizat" and s > c["min_servers"]:
            return -1
        return None

    def execute(self, system, delta, t):
        system.servers += delta
        self.k.state["servers"] = system.servers


# ---------------------------------------------------------------- o rulare
def simulate(variant, rng, keep_trace=False):
    system = QueueSystem(rng)
    if variant["controller"] == "adaptive":
        ctrl = QueueController(dict(start_servers=3, min_servers=2, max_servers=8,
                                    queue_high=5, queue_low=1, util_low=0.6))
    else:
        ctrl = FixedController()
    trace = []
    server_steps = 0
    queues = []
    for t in range(STEPS):
        system.step(t)
        if (t + 1) % variant["window"] == 0:
            ctrl.step(system, t)
        server_steps += system.servers
        queues.append(system.queue)
        if keep_trace:
            trace.append((t, system.queue, system.servers))
    metrics = {"queue_mean_after": float(np.mean(queues[PERTURB_AT:])),
               "server_steps": server_steps,
               "n_decisions": len(ctrl.k.history)}
    return (metrics, trace) if keep_trace else metrics


def run_one(scenario, variant, rng, seed):
    return simulate(variant, rng)


def main():
    variants = {"fix": {"controller": "fixed", "window": 20},
                "adaptiv": {"controller": "adaptive", "window": 20}}
    df = run_grid(run_one, {"crestere_cerere": {}}, variants, seeds=list(range(1000, 1020)),
                  out_csv=OUT / "results.csv")

    summ = summarize(df, ["queue_mean_after", "server_steps"])
    print("\nRezultate pe 20 de rulări (medie ± abatere standard):")
    for _, r in summ.iterrows():
        print(f"  {r['variant']:8s}  coadă medie după perturbare: "
              f"{fmt(r['queue_mean_after_mean'], r['queue_mean_after_std'])}   "
              f"server-pași: {fmt(r['server_steps_mean'], r['server_steps_std'], 0)}")

    # figură cu o rulare demonstrativă din fiecare variantă
    import matplotlib.pyplot as plt
    setup_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 4.5))
    for name, v in variants.items():
        _, tr = simulate(v, np.random.default_rng(1000), keep_trace=True)
        tr = np.array(tr)
        ax1.plot(tr[:, 0], tr[:, 1], label=name, lw=1)
        ax2.step(tr[:, 0], tr[:, 2], label=name, where="post")
    for ax in (ax1, ax2):
        ax.axvline(PERTURB_AT, color="grey", ls="--", lw=0.8)
    ax1.set_ylabel("Lungimea cozii [cereri]")
    ax2.set_ylabel("Servere active")
    ax2.set_xlabel("Pas de simulare")
    ax1.set_title("Răspunsul la creșterea cererii (linia punctată)")
    ax1.legend()
    savefig(fig, OUT / "toy_trace")
    print(f"\nFigura: {OUT / 'toy_trace.pdf'}   Date brute: {OUT / 'results.csv'}")


if __name__ == "__main__":
    main()
