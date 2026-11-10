"""Pregătește datele pentru P2.

Pachetul disciplinei (folderul p2_portofoliu/) conține instanțele oficiale și
șablonul de scenarii; copiați-l în data/p2_portofoliu/. Până îl aveți, sau ca
să testați pe probleme de alte dimensiuni, scriptul acesta generează instanțe
de dezvoltare SINTETICE în data/dev/:

    python scripts/prepare_data.py               # toate instanțele de dezvoltare
    python scripts/prepare_data.py --seed 7      # alt set

Valorile generate sunt inventate; nu le folosiți în raport ca date reale.
Experimentele finale se fac pe instanțele din pachet.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

OUT = Path("data/dev")

KINDS_A = ["bandă de biciclete", "reglarea semafoarelor", "reorganizarea intersecției",
           "trecere de pietoni semaforizată", "stație de autobuz accesibilă", "zonă 30",
           "parcare de transfer", "pistă pietonală"]


def gen_A(n, rng, budget_ratio=0.4):
    cost = np.round(rng.lognormal(mean=np.log(300_000), sigma=0.8, size=n), -3)
    benefit = np.round(cost * rng.uniform(0.6, 2.2, n) / 1000, 1)       # unități de beneficiu
    equity = np.round(rng.beta(2, 3, n) * benefit, 1)
    items = [{"id": f"S{i + 1:02d}", "label": f"{KINDS_A[i % len(KINDS_A)]} #{i + 1}",
              "cost": float(cost[i]), "benefit": float(benefit[i]), "equity": float(equity[i])}
             for i in range(n)]
    return {"name": f"dev_A_{n}", "kind": "binary", "branch": "A",
            "units": {"cost": "EUR", "benefit": "unități de beneficiu (sintetic)", "equity": "unități (sintetic)"},
            "budget": float(np.round(budget_ratio * cost.sum(), -3)), "items": items}


def gen_B(n_lines, rng, fleet_ratio=0.75):
    modes = ["tramvai", "troleibuz", "autobuz"]
    items = []
    for i in range(n_lines):
        lower = int(rng.integers(4, 10))
        upper = lower + int(rng.integers(10, 30))
        items.append({"id": f"L{i + 1:02d}", "label": f"linia {i + 1} ({modes[i % 3]})",
                      "lower": lower, "upper": upper,
                      "benefit": float(np.round(rng.uniform(200, 1200), 0)),       # a_i
                      "saturation": float(np.round(rng.uniform(5, 20), 1)),        # b_i
                      "equity": float(np.round(rng.uniform(0, 1), 2))})
    fleet = int(fleet_ratio * sum(it["upper"] for it in items))
    return {"name": f"dev_B_{n_lines}", "kind": "integer", "branch": "B",
            "units": {"x": "ore-vehicul în fereastra de vârf", "benefit": "pasageri-ore (sintetic)"},
            "budget": fleet, "items": items}


def gen_C(n_zones, rng, phases=2, budget_ratio=0.45):
    items = []
    for z in range(n_zones):
        prev = None
        for ph in range(1, phases + 1):
            km = float(np.round(rng.uniform(0.5, 4.0), 1))
            cost = float(np.round(km * rng.uniform(80_000, 160_000), -3))
            it = {"id": f"Z{z + 1:02d}F{ph}", "label": f"zona {z + 1}, faza {ph}", "km": km,
                  "cost": cost, "benefit": float(np.round(km * rng.uniform(20, 60) / ph, 1)),
                  "equity": float(np.round(rng.uniform(0, 1) * km * 10, 1))}
            if prev:
                it["requires"] = prev                 # faza 2 cere faza 1
            items.append(it)
            prev = it["id"]
    total = sum(it["cost"] for it in items)
    return {"name": f"dev_C_{len(items)}", "kind": "binary", "branch": "C",
            "units": {"cost": "EUR", "km": "km de pistă"},
            "budget": float(np.round(budget_ratio * total, -3)), "items": items}


def changes(inst, rng, gens=(100, 200, 300)):
    # se elimină elementul cu cel mai bun raport beneficiu/cost: aproape sigur face parte
    # din soluția bună de dinainte, deci schimbarea chiar contează
    ratio = [it["benefit"] / it.get("cost", 1.0) for it in inst["items"]]
    removable = inst["items"][int(np.argmax(ratio))]["id"]
    return {"instance": inst["name"], "changes": [
        {"generation": gens[0], "type": "budget_scale", "factor": 0.7},
        {"generation": gens[1], "type": "remove_item", "id": str(removable)},
        {"generation": gens[2], "type": "weights", "w_benefit": 0.5, "w_equity": 0.5}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    OUT.mkdir(parents=True, exist_ok=True)
    for inst in [gen_A(12, rng), gen_A(20, rng), gen_A(40, rng), gen_B(12, rng), gen_C(10, rng)]:
        (OUT / f"{inst['name']}.json").write_text(json.dumps(inst, ensure_ascii=False, indent=1), encoding="utf-8")
        ch = changes(inst, rng)
        (OUT / f"changes_{inst['name']}.json").write_text(json.dumps(ch, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {inst['name']:12s}  n = {len(inst['items']):3d}  buget = {inst['budget']:,.0f}")
    print(f"\nInstanțe SINTETICE de dezvoltare în {OUT}/. Pentru experimentele finale folosiți data/p2_portofoliu/.")
    if not Path("data/p2_portofoliu").exists():
        print("Încă nu ați copiat pachetul disciplinei în data/p2_portofoliu/.")


if __name__ == "__main__":
    main()
