"""Exemplu de export al unei simulări pentru șablon: scrie sablon/sim.js.

    python exemplu_sim.py
    python exemplu_sim.py --vehicule 300 --out ../../../repo/vizualizare/sim.js

Simularea e de jucărie: mașini cu origine și destinație aleatoare merg pe drumul cel mai
rapid. La minutul 20 Bega iese din albie (faza 1 din scenariul coridor_inundatie), la minutul
40 apa crește (faza 2). O mașină care ajunge în fața unei străzi închise își recalculează drumul
din nodul în care se află. Dacă nu mai are drum, rămâne blocată.

Ce contează aici e FORMATUL, pe care îl produceți la fel din simularea voastră:

    window.SIM = {
      descriere: "...",
      durata_s: 3600,
      vehicule: [{id, puncte: [[t_s, nod], [t_s, nod], ...], stare}],   // nod = id ca în retea.graphml
      evenimente: [{t_s, text, inchise: [[u, v], ...], redeschise: [[u, v], ...]}]
    }

Pagina interpolează poziția între două puncte consecutive după timp. Nu contează cum ați
calculat punctele: drum minim, SUMO, un controller care redirecționează. Pagina doar le redă.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# în folderul de resurse baza e în comun/timisoara/; după instalare, în data/timisoara/ din repo
BAZA = next((p for p in (HERE.parent / "timisoara" / "timisoara.sqlite", HERE.parent / "data" / "timisoara" / "timisoara.sqlite")
             if p.exists()), HERE.parent / "data" / "timisoara" / "timisoara.sqlite")
sys.path.insert(0, str(HERE))
from exporta_harta import drum_minim  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=str(BAZA))
    ap.add_argument("--out", default=str(HERE / "sablon" / "sim.js"))
    ap.add_argument("--vehicule", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    con = sqlite3.connect(a.baza)
    timp = {(u, v): max(t, 0.1) for u, v, t in con.execute("select u, v, timp_s from retea_muchii")}
    noduri = [n for (n,) in con.execute("select node from retea_noduri")]
    faze = {}
    for f, u, v in con.execute("select faza, u, v from scenarii_defect where scenariu = 'coridor_inundatie'"):
        faze.setdefault(f, []).append((u, v))
    evenimente = [
        {"t_s": 1200, "text": f"Bega iese din albie: {len(faze[1])} muchii închise", "inchise": faze[1], "redeschise": []},
        {"t_s": 2400, "text": f"apa crește: încă {len(faze[2])} muchii închise", "inchise": faze[2], "redeschise": []},
    ]

    def inchise_la(t):
        s = set()
        for e in evenimente:
            if e["t_s"] <= t:
                s.update(map(tuple, e["inchise"]))
        return s

    def adj_fara(inchise):
        adj = {}
        for (u, v), w in timp.items():
            if (u, v) not in inchise:
                adj.setdefault(u, []).append((v, w))
        return adj

    rnd = random.Random(a.seed)
    cache = {}
    vehicule = []
    for k in range(a.vehicule):
        t = rnd.uniform(0, 2400)
        o, d = rnd.choice(noduri), rnd.choice(noduri)
        puncte, stare, nod = [[round(t, 1), o]], "ajuns", o
        inchise = inchise_la(t)
        drum = drum_minim(cache.setdefault(len(inchise), adj_fara(inchise)), o, d)
        if not drum or len(drum) < 6:
            continue
        i = 0
        while nod != d:
            urm = drum[i + 1]
            inchise = inchise_la(t)
            if (nod, urm) in inchise:                      # strada din față s-a închis: drum nou de aici
                drum = drum_minim(cache.setdefault(len(inchise), adj_fara(inchise)), nod, d)
                stare = "redirecționat"
                if not drum:
                    stare = "blocat"
                    break
                i = 0
                continue
            t += timp[(nod, urm)]
            nod, i = urm, i + 1
            puncte.append([round(t, 1), nod])
        vehicule.append({"id": f"m{k}", "puncte": puncte, "stare": stare})

    data = {"descriere": "Exemplu: inundație pe Bega, mașinile își recalculează drumul",
            "durata_s": 3600 + 1200, "vehicule": vehicule, "evenimente": evenimente}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.SIM = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    nr = {s: sum(v["stare"] == s for v in vehicule) for s in ("ajuns", "redirecționat", "blocat")}
    print(f"Scris {out} ({out.stat().st_size / 1e6:.1f} MB): {len(vehicule)} vehicule {nr}, {len(evenimente)} evenimente")


if __name__ == "__main__":
    main()
