"""Exportă harta Timișoarei din timisoara.sqlite într-un fișier JS pe care îl citește index.html.

    python exporta_harta.py                         # baza de lângă (../timisoara/timisoara.sqlite)
    python exporta_harta.py --baza data/timisoara/timisoara.sqlite --out vizualizare/sablon/date_harta.js

De ce un fișier .js și nu .json: o pagină deschisă direct din disc (file://) nu are voie să
citească fișiere cu fetch(), dar poate încărca un <script src="...">. Așa merge și fără server.
Cu server (python -m http.server), puteți folosi și JSON.

Ce scrie în window.HARTA:
    noduri      [[lon, lat], ...]                     indexul e folosit în muchii și trasee
    ids         ["115", "117", ...]                   id-ul OSM al fiecărui nod, ca în retea.graphml
    muchii      [[i, j, lungime_m, timp_s, importanta, nume], ...]   i, j = indici în noduri
    cartiere    [{nume, populatie, acces_slab, inel: [[lon, lat], ...]}, ...]
    statii      [[lon, lat, nume, nr_linii], ...]
    spitale     [[lon, lat, nume], ...]
    trasee      [[i0, i1, i2, ...], ...]             câteva drumuri minime, doar ca exemplu de
                                                     ce exportați voi din simulare (mașinile din șablon
                                                     circulă pe ele)
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


def inel_din_wkt(wkt: str):
    """Primul inel exterior dintr-un POLYGON / MULTIPOLYGON în WKT (fără shapely)."""
    corp = wkt[wkt.index("(") :].lstrip("(")
    primul = corp.split(")")[0]
    return [[round(float(a), 5), round(float(b), 5)] for a, b in (p.split() for p in primul.split(","))]


def drum_minim(adj, start, stop):
    """Dijkstra simplu pe timp de parcurs (fără networkx, ca scriptul să meargă oriunde)."""
    import heapq
    dist, prev, q = {start: 0.0}, {}, [(0.0, start)]
    while q:
        d, u = heapq.heappop(q)
        if u == stop:
            break
        if d > dist.get(u, 1e18):
            continue
        for v, w in adj.get(u, ()):
            if d + w < dist.get(v, 1e18):
                dist[v], prev[v] = d + w, u
                heapq.heappush(q, (d + w, v))
    if stop not in dist:
        return None
    path = [stop]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return path[::-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=str(BAZA))
    ap.add_argument("--out", default=str(HERE / "sablon" / "date_harta.js"))
    ap.add_argument("--trasee", type=int, default=60, help="câte drumuri de exemplu pentru mașini")
    a = ap.parse_args()
    if not Path(a.baza).exists():
        sys.exit(f"Nu găsesc baza {a.baza}. Instalați-o cu: python instaleaza.py timisoara <repo>")
    con = sqlite3.connect(a.baza)
    noduri = con.execute("select node, lon, lat from retea_noduri").fetchall()
    idx = {n: k for k, (n, _, _) in enumerate(noduri)}
    muchii = []
    for u, v, lung, timp, imp, nume in con.execute(
            "select u, v, lungime_m, timp_s, importanta, nume from retea_muchii"):
        if nume and nume.startswith("["):        # OSM: unele străzi au mai multe nume
            nume = nume.strip("[]").split(",")[0].strip(" '\"")
        muchii.append([idx[u], idx[v], round(lung, 1), round(timp, 1), round(imp or 0, 5), nume or ""])
    cartiere = [{"nume": n, "populatie": int(p), "acces_slab": int(s), "inel": inel_din_wkt(w)}
                for n, p, s, w in con.execute("select cartier, populatie, acces_slab, geometrie_wkt from cartiere")]
    statii = [[round(lo, 5), round(la, 5), n, k] for n, lo, la, k in con.execute(
        "select stop_name, avg(stop_lon), avg(stop_lat), count(distinct route_id) from statii_linii group by stop_name")]
    spitale = [[lo, la, n] for n, lo, la in con.execute("select nume, lon, lat from spitale where tip = 'hospital'")]

    adj = {}
    for i, j, _, t, _, _ in muchii:
        adj.setdefault(i, []).append((j, max(t, 0.1)))
    rnd = random.Random(1)
    trasee = []
    while len(trasee) < a.trasee:
        p = drum_minim(adj, rnd.randrange(len(noduri)), rnd.randrange(len(noduri)))
        if p and len(p) > 8:
            trasee.append(p)
    data = {"noduri": [[round(lo, 6), round(la, 6)] for _, lo, la in noduri],
            "ids": [str(n) for n, _, _ in noduri], "muchii": muchii,
            "cartiere": cartiere, "statii": statii, "spitale": spitale, "trasee": trasee,
            "sursa": "© OpenStreetMap contributors (ODbL); GTFS STPT/SMTT. Populația e estimare de model."}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.HARTA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    print(f"Scris {out} ({out.stat().st_size / 1e6:.1f} MB): {len(noduri)} noduri, {len(muchii)} muchii, "
          f"{len(cartiere)} cartiere, {len(statii)} stații, {len(trasee)} trasee de exemplu")


if __name__ == "__main__":
    main()
