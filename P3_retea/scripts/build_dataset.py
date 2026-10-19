"""Construiește setul de date al temei din OpenStreetMap, în locul pachetului
`p3_retea/` al disciplinei (care nu e încă disponibil).

    python scripts/build_dataset.py                 # parametrii din config (osm:, dataset:)

Produce în data/p3_retea/:
    retea.graphml            graful rutier (componenta tare conexă, intersecții unite la 15 m),
                             cu `population` pe noduri (estimare din clădirile OSM, vedeți mai jos)
    scenarii_defect.json     cele trei scenarii de defect în grup, construite geometric:
                             coridor_inundatie (zona inundabilă a Begăi, în trei faze),
                             traversari_rau (toate muchiile care traversează Bega),
                             coridor_central (axa centrală, Piața Unirii – Piața Victoriei – Catedrală)
    prioritare.csv           perechile prioritare: cartiere -> spitale, gară -> spitale
    importanta_muchii.csv    edge betweenness exact, ponderat cu lungimea
    context.geojson          râul, spitalele și gara (pentru hărți și vizualizare)

Populația pe noduri e un MODEL, nu o măsurătoare: suprafața desfășurată a clădirilor
rezidențiale (amprentă × etaje; 4 etaje dacă lipsește `building:levels` la blocuri,
1 la case) împărțită la 30 m²/locuitor, atribuită nodului celui mai apropiat.

Datele OSM: © OpenStreetMap contributors, licența ODbL.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from sada.config import load_config

RESIDENTIAL = {"apartments", "residential", "house", "detached", "semidetached_house", "terrace",
               "dormitory", "bungalow"}
DEFAULT_LEVELS = {"house": 1, "detached": 1, "semidetached_house": 1, "terrace": 2, "bungalow": 1}


def _levels(row) -> float:
    try:
        v = float(str(row.get("building:levels")).split(";")[0])
        if 0 < v < 40:
            return v
    except (TypeError, ValueError):
        pass
    return DEFAULT_LEVELS.get(row["building"], 4)


def download_graph(center, dist, tolerance):
    G = ox.graph_from_point(center, dist=dist, network_type="drive", simplify=True)
    Gp = ox.project_graph(G)
    Gp = ox.consolidate_intersections(Gp, tolerance=tolerance, rebuild_graph=True, dead_ends=False)
    Gp = ox.truncate.largest_component(Gp, strongly=True)
    Gp = ox.routing.add_edge_speeds(Gp)
    Gp = ox.routing.add_edge_travel_times(Gp)
    return Gp


def edge_lines(Gp) -> gpd.GeoDataFrame:
    """Muchiile grafului proiectat, cu geometria (dreaptă între noduri dacă lipsește)."""
    rows = []
    for u, v, k, d in Gp.edges(keys=True, data=True):
        geom = d.get("geometry") or LineString([(Gp.nodes[u]["x"], Gp.nodes[u]["y"]),
                                                (Gp.nodes[v]["x"], Gp.nodes[v]["y"])])
        rows.append({"u": u, "v": v, "key": k, "geometry": geom, "bridge": d.get("bridge")})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=Gp.graph["crs"])


def add_population(Gp, center, dist, m2_per_person):
    b = ox.features_from_point(center, tags={"building": True}, dist=dist + 200)
    b = b[b.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    b = b[b["building"].isin(RESIDENTIAL | {"yes"})].copy()
    # „yes” e ambiguu (blocuri și clădiri publice); îl numărăm doar dacă are etaje declarate
    has_lv = b.get("building:levels")
    if has_lv is not None:
        b = b[(b["building"] != "yes") | b["building:levels"].notna()]
    else:
        b = b[b["building"] != "yes"]
    b = b.to_crs(Gp.graph["crs"])
    floor = b.geometry.area * b.apply(_levels, axis=1)
    pop = floor / m2_per_person
    nodes = list(Gp.nodes)
    xy = np.array([[Gp.nodes[n]["x"], Gp.nodes[n]["y"]] for n in nodes])
    cent = np.column_stack([b.geometry.centroid.x, b.geometry.centroid.y])
    from scipy.spatial import cKDTree
    dist_nn, idx = cKDTree(xy).query(cent)
    keep = dist_nn < 400          # clădirile de la marginea zonei, fără nod apropiat, nu contează
    acc = np.bincount(idx[keep], weights=pop.to_numpy()[keep], minlength=len(nodes))
    for n, p in zip(nodes, acc):
        Gp.nodes[n]["population"] = float(round(p, 1))
    return int(len(b)), float(acc.sum())


def river_geometry(center, dist, crs, name):
    w = ox.features_from_point(center, tags={"waterway": ["river", "canal"]}, dist=dist + 500)
    w = w[w.geometry.geom_type.isin(["LineString", "MultiLineString"])]
    if name:
        w = w[w.get("name", pd.Series(dtype=str)).fillna("").str.contains(name, case=False)]
    return unary_union(list(w.to_crs(crs).geometry))


def nearest_node(Gp, x, y):
    return min(Gp.nodes, key=lambda n: (Gp.nodes[n]["x"] - x) ** 2 + (Gp.nodes[n]["y"] - y) ** 2)


def project_point(lat, lon, crs):
    return gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(crs).iloc[0]


def main():
    cfg = load_config("config/default.yaml")
    osm, ds = cfg["osm"], cfg["dataset"]
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", type=float, default=osm["dist_m"])
    ap.add_argument("--out", default="data/p3_retea")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = True
    ox.settings.log_console = False
    center = tuple(osm["center"])

    print(f"1. Rețeaua rutieră, raza {a.dist:.0f} m în jurul {center}")
    Gp = download_graph(center, a.dist, osm["consolidate_tolerance_m"])
    print(f"   {Gp.number_of_nodes()} noduri, {Gp.number_of_edges()} muchii (tare conex)")
    crs = Gp.graph["crs"]

    print("2. Populația (din clădirile rezidențiale OSM)")
    nb, tot = add_population(Gp, center, a.dist, ds["m2_per_person"])
    print(f"   {nb} clădiri, populație estimată {tot:,.0f} locuitori")

    print("3. Scenariile de defect în grup")
    E = edge_lines(Gp)
    river = river_geometry(center, a.dist, crs, ds["river_name"])
    dist_r = E.geometry.distance(river)
    # traversările: muchiile care intersectează albia, plus podurile marcate în OSM lângă albie
    # (după unirea intersecțiilor, geometria unor poduri se oprește chiar la mal)
    bridge = E["bridge"].astype(str).str.contains("yes")
    crossing = E.geometry.intersects(river) | (bridge & (dist_r <= 60))
    c0 = project_point(*center, crs)
    near_c = E.geometry.distance(c0) <= ds["crossings_radius_m"]
    trav = E[crossing & near_c]
    # inundația: doar tronsonul din aval (estul orașului), cu apa care crește în faze
    lon0, lon1 = ds["flood_stretch_lon"]
    x0, x1 = project_point(center[0], lon0, crs).x, project_point(center[0], lon1, crs).x
    mid_x = E.geometry.centroid.x
    stretch = (mid_x >= x0) & (mid_x <= x1)
    flood_phases = []
    prev = set()
    for d in ds["flood_phases_m"]:
        cur = set(map(tuple, E[(dist_r <= d) & stretch][["u", "v", "key"]].itertuples(index=False, name=None)))
        flood_phases.append(sorted(cur - prev))
        prev |= cur
    pts = [project_point(lat, lon, crs) for lat, lon in ds["central_axis"]]
    axis = LineString([(p.x, p.y) for p in pts])
    central = E[E.geometry.distance(axis) <= ds["central_buffer_m"]]
    m = Gp.number_of_edges()
    scen = {
        "coridor_inundatie": {
            "descriere": f"Zona inundabilă a râului {ds['river_name']} pe tronsonul din aval (est, "
                         f"longitudine {lon0}–{lon1}): apa crește în {len(flood_phases)} faze "
                         f"(muchii la cel mult {ds['flood_phases_m']} m de albie).",
            "faze": [[list(e) for e in ph] for ph in flood_phases]},
        "traversari_rau": {
            "descriere": f"Podurile peste {ds['river_name']} din centru (la cel mult "
                         f"{ds['crossings_radius_m']} m de Piața Victoriei) închise; podurile periferice rămân.",
            "muchii": [list(e) for e in trav[["u", "v", "key"]].itertuples(index=False, name=None)]},
        "coridor_central": {
            "descriere": f"Axa centrală Piața Unirii – Piața Victoriei – Catedrală, zonă de "
                         f"{ds['central_buffer_m']} m de o parte și de alta (eveniment, lucrări).",
            "muchii": [list(e) for e in central[["u", "v", "key"]].itertuples(index=False, name=None)]},
    }
    for k, s in scen.items():
        n = sum(len(f) for f in s["faze"]) if "faze" in s else len(s["muchii"])
        print(f"   {k}: {n} muchii ({100 * n / m:.1f}%)")
    meta = {"_format": "muchii = [u, v, cheie] în retea.graphml; faze = listă de liste, aplicate pe rând",
            "_sursa": f"OpenStreetMap (ODbL), construit cu scripts/build_dataset.py la {dt.date.today()}"}
    (out / "scenarii_defect.json").write_text(json.dumps({**meta, **scen}, ensure_ascii=False, indent=1),
                                              encoding="utf-8")

    print("4. Perechile prioritare (spitale, gară)")
    hosp = ox.features_from_point(center, tags={"amenity": "hospital"}, dist=a.dist)
    hosp = hosp.to_crs(crs)
    # amenity=hospital include și cabinete mici; păstrăm spitalele mari (după suprafața amprentei)
    hosp = hosp[hosp.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    hosp["area"] = hosp.geometry.area
    hosp = hosp[hosp["area"] >= ds["hospital_min_area_m2"]].sort_values("area", ascending=False)
    hosp["pt"] = hosp.geometry.centroid
    hnodes = []
    for _, h in hosp.iterrows():
        n = nearest_node(Gp, h.pt.x, h.pt.y)
        if n not in [x[0] for x in hnodes]:
            nm = h.get("name")
            hnodes.append((n, nm if isinstance(nm, str) else "spital (fără nume în OSM)"))
    st = project_point(*ds["station"], crs)
    station = nearest_node(Gp, st.x, st.y)
    rng = np.random.default_rng(ds["seed"])
    nodes = list(Gp.nodes)
    w = np.array([Gp.nodes[n]["population"] for n in nodes])
    w = w / w.sum()
    rows = []
    for hn, hname in hnodes[: ds["max_hospitals"]]:
        for o in rng.choice(len(nodes), size=ds["pairs_per_hospital"], replace=False, p=w):
            if nodes[o] != hn:
                rows.append({"origin": nodes[o], "destination": hn, "tip": f"cartier -> {hname}"})
        if hn != station:
            rows.append({"origin": station, "destination": hn, "tip": f"gară -> {hname}"})
    pd.DataFrame(rows).drop_duplicates(["origin", "destination"]).to_csv(out / "prioritare.csv", index=False)
    print(f"   {len(hnodes)} spitale în zonă, {len(rows)} perechi prioritare")

    print("5. Importanța muchiilor (edge betweenness exact, ponderat cu lungimea)")
    imp = nx.edge_betweenness_centrality(Gp, weight="length")
    df = pd.DataFrame([{"u": u, "v": v, "key": k, "importance": val} for (u, v, k), val in imp.items()])
    df.sort_values("importance", ascending=False).to_csv(out / "importanta_muchii.csv", index=False)

    print("6. Contextul pentru hărți și salvarea grafului")
    ctx = []
    rv = gpd.GeoSeries([river], crs=crs).to_crs("EPSG:4326").iloc[0]
    ctx.append({"type": "Feature", "properties": {"kind": "river", "name": ds["river_name"]},
                "geometry": json.loads(gpd.GeoSeries([rv]).to_json())["features"][0]["geometry"]})
    for hn, hname in hnodes:
        ctx.append({"type": "Feature", "properties": {"kind": "hospital", "name": hname, "node": hn},
                    "geometry": {"type": "Point", "coordinates": [0, 0]}})
    ctx.append({"type": "Feature", "properties": {"kind": "station", "name": "Gara Timișoara Nord", "node": station},
                "geometry": {"type": "Point", "coordinates": [0, 0]}})
    G = ox.project_graph(Gp, to_latlong=True)
    for f in ctx:
        n = f["properties"].get("node")
        if n is not None:
            f["geometry"]["coordinates"] = [G.nodes[n]["x"], G.nodes[n]["y"]]
    (out / "context.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": ctx},
                                                    ensure_ascii=False), encoding="utf-8")
    ox.save_graphml(G, out / "retea.graphml")
    print(f"Salvat în {out}/. Pasul următor: python scripts/prepare_od.py")


if __name__ == "__main__":
    main()
