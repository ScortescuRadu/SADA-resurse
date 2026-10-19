"""Exemplu de export pentru P1 (coridorul cu automate celulare): scrie sablon/coridor_date.js,
pe care îl desenează sablon/coridor.html.

    python exemplu_coridor.py

Formatul e matricea benzi × celule pe care o țineți oricum în Corridor (viteza, -1 pentru
celulă goală), scrisă la fiecare pas ca un șir de caractere: '.' = gol, '0'..'9' = viteza.
Banda 0 e prima, apoi banda 1 și așa mai departe. Pentru 3 benzi × 400 de celule, un pas are
1200 de caractere; 1200 de pași fac ~1,5 MB, deci merge fără probleme într-un fișier .js.

În simularea voastră, adăugați la fiecare pas:

    rand = "".join("." if v < 0 else str(v) for v in grila.ravel())   # grila: benzi × celule
    pasi.append(rand)

și la final scrieți fișierul ca mai jos (scrie_js). Evenimentele (începe incidentul, controllerul
schimbă regula pe un tronson) le adăugați în `evenimente` cu pasul la care s-au întâmplat.

ATENȚIE: modelul de aici NU e NaSch. N-are încetinire aleatoare și nici schimbare de bandă,
deci coada se formează doar pe banda incidentului. E doar ca să aveți ce desena.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def scrie_js(path, **date):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("window.CORIDOR = " + json.dumps(date, ensure_ascii=False, separators=(",", ":")) + ";\n",
                    encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "sablon" / "coridor_date.js"))
    ap.add_argument("--pasi", type=int, default=1200)
    a = ap.parse_args()
    benzi, celule, vmax, cell_m, dt_s, tronson = 3, 400, 2, 7.5, 1.0, 40
    debit = 0.28                                   # probabilitatea de intrare pe bandă, pe pas
    inc = {"banda": 0, "celula": 300, "de_la": 200, "pana_la": 650}
    rnd = random.Random(3)
    grila = [[-1] * celule for _ in range(benzi)]
    pasi, evenimente = [], []
    for t in range(a.pasi):
        if t == inc["de_la"]:
            evenimente.append({"pas": t, "text": f"incident: banda {inc['banda']}, celula {inc['celula']} blocată"})
        if t == inc["pana_la"]:
            evenimente.append({"pas": t, "text": "incidentul s-a terminat"})
        blocat = inc["de_la"] <= t < inc["pana_la"]
        for b in range(benzi):
            row, nou = grila[b], [-1] * celule
            ocupate = [c for c in range(celule) if row[c] >= 0]
            for k, c in enumerate(ocupate):
                fata = ocupate[k + 1] if k + 1 < len(ocupate) else celule + vmax + 1
                if blocat and b == inc["banda"] and c < inc["celula"]:
                    fata = min(fata, inc["celula"])
                v = min(row[c] + 1, vmax, fata - c - 1)   # accelerează, dar nu intră în cel din față
                if c + v < celule:
                    nou[c + v] = v
            if nou[0] < 0 and rnd.random() < debit:
                nou[0] = 1
            grila[b] = nou
        pasi.append("".join("." if v < 0 else str(v) for row in grila for v in row))
    out = scrie_js(a.out, benzi=benzi, celule=celule, vmax=vmax, cell_m=cell_m, dt_s=dt_s,
                   tronson_celule=tronson, incident=inc, evenimente=evenimente, pasi=pasi,
                   descriere="Exemplu: incident pe banda 0 (model simplificat, fără NaSch)")
    print(f"Scris {out} ({out.stat().st_size / 1e6:.1f} MB): {len(pasi)} pași, {benzi} benzi × {celule} celule")


if __name__ == "__main__":
    main()
