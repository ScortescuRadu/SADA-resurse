"""Reface timisoara.sqlite din datele din folderele P2, P3 și P4 de alături.

    python comun/timisoara/fa_baza.py          (din rădăcina folderului de resurse)

Nu trebuie să-l rulați: baza e deja făcută. E aici ca să se vadă de unde vine fiecare tabel.
Are nevoie de pandas, networkx, geopandas și shapely (toate sunt în mediile din kituri, plus
geopandas: pip install geopandas).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "timisoara.sqlite"
P2 = ROOT / "P2_portofoliu/data"
P3 = ROOT / "P3_retea/data/p3_retea"
P4 = ROOT / "P4_transport/data/p4_gtfs"

SURSE = [
    ("populatie", "clădirile OpenStreetMap (ODbL, © OpenStreetMap contributors)",
     "MODEL: suprafața desfășurată a clădirilor rezidențiale / 30 m² pe locuitor, grilă de 200 m"),
    ("cartiere", "OSM place=suburb/quarter/neighbourhood (ODbL)",
     "celule Voronoi pe grila de populație; acoperire_s0 = partea din populație la ≤ 400 m de o stație cu interval ≤ 20 min"),
    ("statii_linii", "GTFS STPT/SMTT, Mobility Database mdb-2868, miercuri 2026-10-14", "intervalul mediu pe sens, 07:00–09:00"),
    ("incarcari", "MODEL de cerere (P4_transport/scripts/build_dataset.py)", "nu sunt validări de bilete"),
    ("capacitati", "ipoteze (fișe tehnice tipice)", "locuri pe vehicul"),
    ("interventii", "P2_portofoliu/scripts/build_portfolio.py", "costuri și beneficii din MODEL; locații reale"),
    ("interactiuni", "P2_portofoliu/scripts/build_portfolio.py", "beneficiul pierdut când două intervenții acoperă aceeași populație"),
    ("instante_p2", "P2_portofoliu/scripts/build_portfolio.py", "bugetul instanțelor tm_A_40 și tm_A_20"),
    ("retea_noduri", "OpenStreetMap prin OSMnx, raza 2500 m în jurul Pieței Victoriei (ODbL)",
     "intersecții unite la 15 m; componenta tare conexă; population = MODEL"),
    ("retea_muchii", "OpenStreetMap prin OSMnx, raza 2500 m în jurul Pieței Victoriei (ODbL)",
     "importanta = edge betweenness exact ponderat cu lungimea"),
    ("scenarii_defect", "derivat geometric din graf și albia Begăi (OSM)", "ipotetice"),
    ("spitale", "OSM amenity=hospital, amprentă ≥ 3000 m²; gara Timișoara Nord",
     "tip = hospital sau station; node = nodul cel mai apropiat din retea_noduri"),
    ("perechi_prioritare", "P3_retea/scripts/build_dataset.py", "cartiere și gară -> spitale; noduri din retea_noduri"),
    ("surse", "—", "tabelul acesta"),
]


def wkt_wgs84(path, simplify_m=25):
    g = gpd.read_file(path).to_crs(3844)
    g["geometry"] = g.geometry.simplify(simplify_m)
    return g.to_crs(4326)


def main():
    if OUT.exists():
        OUT.unlink()
    con = sqlite3.connect(OUT)

    pop = pd.read_csv(P4 / "populatie_grila.csv").rename(columns={"zone": "cartier", "population": "populatie"})
    pop.to_sql("populatie", con, index=False)

    z = wkt_wgs84(P4 / "zone.geojson")
    weak = set(gpd.read_file(P4 / "zone_acces_slab.geojson")["zone"])
    pd.DataFrame({"cartier": z["zone"], "populatie": z["population"], "acoperire_s0": z["coverage_s0"],
                  "acces_slab": z["zone"].isin(weak).astype(int), "geometrie_wkt": z.geometry.to_wkt()}) \
        .to_sql("cartiere", con, index=False)

    pd.read_csv(P4 / "statii_linii.csv", dtype={"stop_id": str}).to_sql("statii_linii", con, index=False)
    pd.read_csv(P4 / "incarcari.csv").rename(columns={"window": "fereastra", "passengers": "pasageri"}) \
        .to_sql("incarcari", con, index=False)
    pd.read_csv(P4 / "capacitati.csv").to_sql("capacitati", con, index=False)

    rows, inter, inst = [], [], []
    for name in ("tm_A_40", "tm_A_20"):
        d = json.loads((P2 / f"p2_portofoliu/{name}.json").read_text(encoding="utf-8"))
        inst.append({"instanta": name, "buget_eur": d["budget"], "n": len(d["items"])})
        if name == "tm_A_40":
            for it in d["items"]:
                line = it.get("line")
                rows.append({"id": it["id"], "tip": it["type"], "eticheta": it["label"], "cost_eur": it["cost"],
                             "beneficiu": it["benefit"], "echitate": it["equity"], "populatie": it["population"],
                             "lon": it["lon"], "lat": it["lat"],
                             "linie_wkt": "LINESTRING (" + ", ".join(f"{a} {b}" for a, b in line) + ")" if line else None})
            inter = [{"i": t["i"], "j": t["j"], "beneficiu_pierdut": t["benefit"], "echitate_pierduta": t["equity"]}
                     for t in d["interactions"]]
        else:
            in20 = {it["id"] for it in d["items"]}
    df = pd.DataFrame(rows)
    df["in_tm_A_20"] = df["id"].isin(in20).astype(int)
    df.to_sql("interventii", con, index=False)
    pd.DataFrame(inter).to_sql("interactiuni", con, index=False)
    pd.DataFrame(inst).to_sql("instante_p2", con, index=False)

    G = nx.read_graphml(P3 / "retea.graphml")
    nodes = [{"node": n, "lon": float(d["x"]), "lat": float(d["y"]), "populatie": float(d.get("population", 0))}
             for n, d in G.nodes(data=True)]
    pd.DataFrame(nodes).to_sql("retea_noduri", con, index=False)
    imp = pd.read_csv(P3 / "importanta_muchii.csv", dtype={"u": str, "v": str})
    imp = {(r.u, r.v, int(r.key)): r.importance for r in imp.itertuples()}
    edges = []
    for u, v, k, d in G.edges(keys=True, data=True):
        name = d.get("name")
        edges.append({"u": u, "v": v, "key": int(k), "lungime_m": float(d.get("length", 0)),
                      "timp_s": float(d.get("travel_time", 0)), "tip_drum": d.get("highway"),
                      "nume": name, "sens_unic": str(d.get("oneway")), "importanta": imp.get((u, v, int(k)))})
    pd.DataFrame(edges).to_sql("retea_muchii", con, index=False)

    sc = json.loads((P3 / "scenarii_defect.json").read_text(encoding="utf-8"))
    srows = []
    for name, s in sc.items():
        if name.startswith("_"):
            continue
        phases = s["faze"] if "faze" in s else [s["muchii"]]
        for f, ph in enumerate(phases, 1):
            srows += [{"scenariu": name, "faza": f, "u": str(u), "v": str(v), "key": int(k)} for u, v, k in ph]
    pd.DataFrame(srows).to_sql("scenarii_defect", con, index=False)

    ctx = json.loads((P3 / "context.geojson").read_text(encoding="utf-8"))
    pd.DataFrame([{"nume": f["properties"]["name"], "tip": f["properties"]["kind"], "node": str(f["properties"]["node"]),
                   "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
                  for f in ctx["features"] if f["properties"]["kind"] != "river"]).to_sql("spitale", con, index=False)
    pd.read_csv(P3 / "prioritare.csv", dtype=str).rename(columns={"origin": "origine", "destination": "destinatie"}) \
        .to_sql("perechi_prioritare", con, index=False)

    pd.DataFrame(SURSE, columns=["tabel", "sursa", "nota"]).to_sql("surse", con, index=False)
    con.execute("VACUUM")
    con.close()
    print(f"Scris {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
