"""Construiește portofoliul de intervenții urbane pentru Timișoara (ramura A), în locul
pachetului `p2_portofoliu/` al disciplinei (care nu e încă disponibil).

    python scripts/build_portfolio.py

Intrări (data/raw/timisoara/, aceleași date ca în resursele P4, din GTFS STPT și OpenStreetMap):
    populatie_grila.csv      grila de 200 m cu populația estimată și cartierul
    statii_linii.csv         stațiile liniilor urbane și intervalul lor în vârful de dimineață
    zone.geojson, zone_acces_slab.geojson   cartierele și cele 6 cu acces slab la transport
Școlile se iau din numele stațiilor GTFS (licee, colegii, facultăți), fără acces la rețea.

Ieșiri (data/p2_portofoliu/):
    tm_A_40.json             40 de intervenții în tot orașul, buget = 35% din costul total
    tm_A_20.json             20 dintre ele (jumătate din fiecare tip), buget = 40% din costul lor
    changes_*.json           scenariile de schimbare (vedeți config/default.yaml, secțiunea portfolio)

MODELUL DE EVALUARE (simplificat; beneficiile NU sunt măsurate):
    cost      = costul unitar al tipului × mărimea (km, intersecții) × un factor lognormal (σ = 0,25)
    beneficiu = Σ populația din zona de influență × efectul tipului
                [mii de ore-persoană echivalente pe an: timp câștigat + siguranța, monetizată în ore]
    echitate  = aceeași sumă, dar numai pentru populația fără acces bun la transport public
                (fără nicio stație cu interval ≤ 20 min la 400 m), dublată în cartierele cu acces slab
    interacțiuni: două intervenții cu zone de influență suprapuse nu își adună integral efectele:
                r_ij = ρ · min(b_i · P_ij / P_i, b_j · P_ij / P_j), unde P_ij e populația comună;
                obiectivul devine Σ b_i x_i − Σ r_ij x_i x_j (la fel pentru echitate), ρ = `redundancy`
Costurile unitare și efectele sunt ipoteze de ordin de mărime, în `config/default.yaml`.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point

from sada.config import load_config

RAW = Path("data/raw/timisoara")
OUT = Path("data/p2_portofoliu")
TO_M = Transformer.from_crs("EPSG:4326", "EPSG:3844", always_xy=True)
TO_LL = Transformer.from_crs("EPSG:3844", "EPSG:4326", always_xy=True)


def far_apart(points, k, min_d, start=()):
    """Primele k puncte (în ordinea dată) aflate la cel puțin min_d de cele deja alese."""
    out = list(start)
    for p in points:
        if all(np.hypot(p[0] - q[0], p[1] - q[1]) >= min_d for q in out):
            out.append(p)
        if len(out) >= k + len(start):
            break
    return out[len(start):]


def catchment(grid, geom, radius):
    """Indicii celulelor de populație aflate la cel mult `radius` m de geometrie."""
    pts = gpd.GeoSeries(gpd.points_from_xy(grid.x_m, grid.y_m), crs=3844)
    return np.where(pts.distance(geom) <= radius)[0]


def main():
    cfg = load_config("config/default.yaml")
    pc = cfg["portfolio"]
    rng = np.random.default_rng(pc["seed"])
    OUT.mkdir(parents=True, exist_ok=True)
    grid = pd.read_csv(RAW / "populatie_grila.csv")
    sr = pd.read_csv(RAW / "statii_linii.csv", dtype={"stop_id": str})
    zones = gpd.read_file(RAW / "zone.geojson").to_crs(3844)
    weak = gpd.read_file(RAW / "zone_acces_slab.geojson").to_crs(3844)

    # acces bun la transport: o stație cu interval ≤ 20 min la 400 m
    ok = sr[sr.headway_min <= 20].drop_duplicates("stop_id")
    d, _ = cKDTree(ok[["x_m", "y_m"]].to_numpy()).query(grid[["x_m", "y_m"]].to_numpy())
    grid["poor"] = (d > 400).astype(float)
    grid["eq_w"] = grid.poor * np.where(grid.zone.isin(set(weak.zone)), 2.0, 1.0)
    print(f"Populație fără acces bun la transport: {grid.population[grid.poor > 0].sum():,.0f} "
          f"din {grid.population.sum():,.0f}")

    T = pc["types"]
    cands = []                 # (tip, nume, geometrie, mărime)
    # intersecțiile cele mai aglomerate: stațiile prin care trec cele mai multe linii
    busy = sr.groupby(["stop_name"]).agg(n=("route_id", "nunique"), x=("x_m", "mean"), y=("y_m", "mean")) \
             .sort_values("n", ascending=False)
    pts = far_apart(list(zip(busy.x, busy.y, busy.index)), T["semafoare"]["count"] + T["intersectie"]["count"], 700)
    for (x, y, nm) in pts[:T["semafoare"]["count"]]:
        cands.append(("semafoare", f"semaforizare adaptivă pe coridorul {nm}", LineString([(x - 600, y), (x + 600, y)]), 4))
    for (x, y, nm) in pts[T["semafoare"]["count"]:]:
        cands.append(("intersectie", f"reorganizarea intersecției {nm}", Point(x, y), 1))
    # școlile: treceri semaforizate și zone 30. Locațiile vin din stațiile GTFS care poartă numele
    # unei școli, licee sau facultăți (sursă locală și reproductibilă; Overpass/OSM nu e necesar)
    pat = r"\bȘcoal|\bScoal|Liceu|Colegi|Grădiniț|Universit|Facultat"
    sch = sr[sr.stop_name.str.contains(pat, case=False, regex=True)].groupby("stop_name")[["x_m", "y_m"]].mean()
    order = rng.permutation(len(sch))
    spts = far_apart([(sch.x_m.iloc[i], sch.y_m.iloc[i], sch.index[i]) for i in order],
                     T["trecere"]["count"] + T["zona30"]["count"], 300)
    for (x, y, nm) in spts[:T["trecere"]["count"]]:
        cands.append(("trecere", f"trecere de pietoni semaforizată la {nm}", Point(x, y), 1))
    for (x, y, nm) in spts[T["trecere"]["count"]:]:
        cands.append(("zona30", f"zonă 30 în jurul {nm}", Point(x, y).buffer(350), 1))
    # stații accesibile: stațiile din cartierele cele mai populate
    zpop = grid.groupby("zone").population.sum().sort_values(ascending=False)
    st = sr.drop_duplicates("stop_name").copy()
    _, gi = cKDTree(grid[["x_m", "y_m"]].to_numpy()).query(st[["x_m", "y_m"]].to_numpy())
    st["zone"] = grid.zone.to_numpy()[gi]          # cartierul celulei de populație celei mai apropiate
    picks = []
    for z in zpop.index:
        s = st[st.zone == z]
        if len(s):
            r = s.iloc[int(rng.integers(len(s)))]
            picks.append((r.x_m, r.y_m, f"{r.stop_name} ({z})"))
        if len(picks) >= T["statie"]["count"]:
            break
    for (x, y, nm) in picks:
        cands.append(("statie", f"stație accesibilă și informare în timp real: {nm}", Point(x, y), 1))
    # benzi de biciclete: între centrele unor cartiere vecine populate
    cent = grid.groupby("zone").apply(lambda g: pd.Series({"x": np.average(g.x_m, weights=g.population),
                                                           "y": np.average(g.y_m, weights=g.population),
                                                           "pop": g.population.sum()}), include_groups=False)
    cent = cent.sort_values("pop", ascending=False).head(18)
    tree = cKDTree(cent[["x", "y"]].to_numpy())
    pairs = set()
    for i, (zn, r) in enumerate(cent.iterrows()):
        _, j = tree.query([r.x, r.y], k=2)
        pairs.add(tuple(sorted((zn, cent.index[j[1]]))))
    for a, b in sorted(pairs)[: T["bicicleta"]["count"]]:       # sortat: reproductibil (ordinea unui set nu e)
        ln = LineString([(cent.loc[a, "x"], cent.loc[a, "y"]), (cent.loc[b, "x"], cent.loc[b, "y"])])
        cands.append(("bicicleta", f"bandă de biciclete protejată {a} – {b}", ln, ln.length / 1000))
    # microbuz în cartierele cu acces slab
    for _, r in weak.head(T["microbuz"]["count"]).iterrows():
        cands.append(("microbuz", f"linie de microbuz de cartier: {r.zone}", r.geometry, 1))
    # parcări de transfer la capetele liniilor (stațiile cele mai depărtate de centru)
    cx, cy = TO_M.transform(pc["center"][1], pc["center"][0])
    term = sr.assign(d=np.hypot(sr.x_m - cx, sr.y_m - cy)).sort_values("d", ascending=False).drop_duplicates("stop_name")
    tpts = far_apart(list(zip(term.x_m, term.y_m, term.stop_name)), T["park_ride"]["count"], 2500)
    for (x, y, nm) in tpts:
        cands.append(("park_ride", f"parcare de transfer (P+R) la {nm}", Point(x, y), 1))

    items, catch = [], []
    for k, (typ, label, geom, size) in enumerate(cands):
        t = T[typ]
        idx = catchment(grid, geom, t["radius_m"])
        pop = grid.population.to_numpy()[idx]
        cost = t["unit_cost"] * size * float(np.exp(rng.normal(0, pc["cost_sigma"])))
        noise = float(np.exp(rng.normal(0, pc["benefit_sigma"])))   # ce nu prinde modelul (trafic, accidente)
        catch.append(idx)
        benefit = pop.sum() * t["effect_h"] / 1000.0 * noise
        equity = (pop * grid.eq_w.to_numpy()[idx]).sum() * t["effect_h"] / 1000.0 * noise
        c = geom.centroid
        lon, lat = TO_LL.transform(c.x, c.y)
        coords = None
        if geom.geom_type == "LineString":
            coords = [list(TO_LL.transform(x, y)) for x, y in geom.coords]
        items.append({"id": f"I{k + 1:02d}", "type": typ, "label": label, "cost": float(round(cost, -3)),
                      "benefit": round(float(benefit), 1), "equity": round(float(equity), 1),
                      "population": int(pop.sum()), "lon": round(lon, 5), "lat": round(lat, 5),
                      **({"line": [[round(a, 5), round(b, 5)] for a, b in coords]} if coords else {})})
    popv, eqw = grid.population.to_numpy(), grid.eq_w.to_numpy()
    inter = []
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            com = np.intersect1d(catch[a], catch[b])
            if not len(com):
                continue
            pa, pb = max(popv[catch[a]].sum(), 1e-9), max(popv[catch[b]].sum(), 1e-9)
            ea = max((popv[catch[a]] * eqw[catch[a]]).sum(), 1e-9)
            eb = max((popv[catch[b]] * eqw[catch[b]]).sum(), 1e-9)
            pc_, pe_ = popv[com].sum(), (popv[com] * eqw[com]).sum()
            rb = pc["redundancy"] * min(items[a]["benefit"] * pc_ / pa, items[b]["benefit"] * pc_ / pb)
            re = pc["redundancy"] * min(items[a]["equity"] * pe_ / ea, items[b]["equity"] * pe_ / eb)
            if rb > 0.05 or re > 0.05:
                inter.append({"i": items[a]["id"], "j": items[b]["id"], "benefit": round(float(rb), 2),
                              "equity": round(float(re), 2)})
    print(f"{len(inter)} perechi de intervenții cu zone de influență suprapuse")
    meta = {"interactions": inter, "units": {"cost": "EUR", "benefit": "mii de ore-persoană echivalente pe an (model)",
                      "equity": "partea din beneficiu care ajunge la populația fără acces bun la transport public, "
                                "dublată în cartierele cu acces slab (model)"},
            "source": "construit cu scripts/build_portfolio.py; vedeți data/DATA.md",
            "note": "Beneficiile și echitatea sunt estimări de model, nu valori măsurate."}
    inst40 = {"name": "tm_A_40", "kind": "binary", "branch": "A", **meta,
              "budget": float(round(pc["budget_ratio_40"] * sum(i["cost"] for i in items), -3)), "items": items}
    sel = []
    for typ in T:
        its = [i for i in items if i["type"] == typ]
        sel += its[: (len(its) + 1) // 2]
    sel = sel[:20]
    inst20 = {"name": "tm_A_20", "kind": "binary", "branch": "A", **meta,
              "budget": float(round(pc["budget_ratio_20"] * sum(i["cost"] for i in sel), -3)), "items": sel}
    for inst in (inst20, inst40):
        (OUT / f"{inst['name']}.json").write_text(json.dumps(inst, ensure_ascii=False, indent=1), encoding="utf-8")
        tc = sum(i["cost"] for i in inst["items"])
        print(f"{inst['name']}: {len(inst['items'])} intervenții, cost total {tc / 1e6:.1f} mil. EUR, "
              f"buget {inst['budget'] / 1e6:.1f} mil. EUR")
    df = pd.DataFrame(items)
    print(df.groupby("type").agg(n=("id", "size"), cost=("cost", "mean"), ben=("benefit", "mean"),
                                 eq=("equity", "mean")).round(1).to_string())
    write_changes(inst20, inst40, pc)


def write_changes(inst20, inst40, pc):
    """Scenariile de schimbare. Intervenția eliminată e cea mai valoroasă din optimul stării
    de dinainte (altfel schimbarea n-ar conta): un aviz de mediu refuzat, de exemplu."""
    from sada.p2.exact import solve
    from sada.p2.problem import Problem
    for inst in (inst20, inst40):
        p = Problem.from_json(OUT / f"{inst['name']}.json")
        g = pc["change_generations"]
        p.apply_change({"type": "budget_scale", "factor": pc["budget_cut"]})
        x, _ = solve(p)
        w = p.w_benefit * p.benefit
        rem = p.ids[int(np.argmax(np.where(x == 1, w, -np.inf)))]
        std = [{"generation": g[0], "type": "budget_scale", "factor": pc["budget_cut"], "motiv": "rectificare bugetară"},
               {"generation": g[1], "type": "remove_item", "id": rem, "motiv": "aviz refuzat"},
               {"generation": g[2], "type": "weights", "w_benefit": 0.5, "w_equity": 0.5,
                "motiv": "consiliul local prioritizează echitatea"}]
        (OUT / f"changes_{inst['name']}.json").write_text(json.dumps({"instance": inst["name"], "changes": std},
                                                                    ensure_ascii=False, indent=1), encoding="utf-8")
        back = [{"generation": g[0], "type": "budget_scale", "factor": pc["budget_cut"], "motiv": "rectificare bugetară"},
                {"generation": g[1], "type": "budget_scale", "factor": round(1 / pc["budget_cut"], 6),
                 "motiv": "bugetul revine (fonduri europene aprobate)"},
                {"generation": g[2], "type": "budget_scale", "factor": pc["budget_cut"], "motiv": "a doua tăiere"}]
        (OUT / f"changes_{inst['name']}_revenire.json").write_text(
            json.dumps({"instance": inst["name"], "changes": back}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {inst['name']}: eliminată la generația {g[1]}: {rem}")


if __name__ == "__main__":
    main()
