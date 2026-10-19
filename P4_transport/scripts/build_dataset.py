"""Construiește datele temei în locul pachetului `p4_gtfs/` al disciplinei (care nu e
disponibil încă): populația, cartierele, zonele cu acces slab, capacitățile,
stațiile pe linii și încărcările.

    python scripts/build_dataset.py          # după scripts/baseline_s0.py

Produce în data/p4_gtfs/:
    populatie_grila.csv     grila de 200 m: x_m, y_m (Stereo 70), lat, lon, populație estimată
    zone.geojson            cartierele (OSM place=suburb/quarter/neighbourhood, celule Voronoi),
                            cu populația și acoperirea în S0
    zone_acces_slab.geojson cartierele cu cea mai mică acoperire în S0
    capacitati.csv          locuri pe vehicul, pe mod (ipoteze, cu sursa)
    statii_linii.csv        stațiile fiecărei linii urbane din fereastră și intervalul ei în S0
    incarcari.csv           MODELUL DE CERERE: pasageri în secțiunea cea mai încărcată, pe linie și
                            fereastră de 15 minute (07:00–09:00)

Populația e un MODEL: suprafața desfășurată a clădirilor rezidențiale OSM / 30 m² pe locuitor.
Încărcările sunt un MODEL, nu validări de bilete (vedeți modelul de cerere mai jos).
Datele OSM: © OpenStreetMap contributors, ODbL.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import Point
from shapely.ops import unary_union

from sada.config import load_config
from sada.p4.baseline import headways, trips_in_window
from sada.p4.gtfs_io import active_service_ids, load_feed, stops_xy

RESIDENTIAL = {"apartments", "residential", "house", "detached", "semidetached_house", "terrace", "dormitory", "bungalow"}
DEFAULT_LEVELS = {"house": 1, "detached": 1, "semidetached_house": 1, "terrace": 2, "bungalow": 1}
EPSG = 3844
TO_M = Transformer.from_crs("EPSG:4326", f"EPSG:{EPSG}", always_xy=True)
TO_LL = Transformer.from_crs(f"EPSG:{EPSG}", "EPSG:4326", always_xy=True)


def levels(row) -> float:
    try:
        v = float(str(row.get("building:levels")).split(";")[0])
        if 0 < v < 40:
            return v
    except (TypeError, ValueError):
        pass
    return DEFAULT_LEVELS.get(row["building"], 4)


def population_grid(center, dist, cell, m2_per_person) -> pd.DataFrame:
    b = ox.features_from_point(center, tags={"building": True}, dist=dist)
    b = b[b.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    lv = b["building:levels"] if "building:levels" in b else pd.Series(np.nan, index=b.index)
    b = b[b["building"].isin(RESIDENTIAL) | ((b["building"] == "yes") & lv.notna())]
    b = b.to_crs(EPSG)
    pop = b.geometry.area * b.apply(levels, axis=1) / m2_per_person
    c = b.geometry.centroid
    gx, gy = np.floor(c.x / cell).astype(int), np.floor(c.y / cell).astype(int)
    df = pd.DataFrame({"gx": gx, "gy": gy, "population": pop}).groupby(["gx", "gy"], as_index=False).sum()
    df["x_m"], df["y_m"] = (df.gx + 0.5) * cell, (df.gy + 0.5) * cell
    df["lon"], df["lat"] = TO_LL.transform(df.x_m.to_numpy(), df.y_m.to_numpy())
    df["population"] = df.population.round(1)
    print(f"   {len(b)} clădiri rezidențiale, {len(df)} celule, {df.population.sum():,.0f} locuitori estimați")
    return df[df.population >= 1][["x_m", "y_m", "lat", "lon", "population"]].reset_index(drop=True)


def zones(center, dist, grid, min_pop) -> gpd.GeoDataFrame:
    p = ox.features_from_point(center, tags={"place": ["suburb", "quarter", "neighbourhood"]}, dist=dist)
    p = p[p.geometry.geom_type == "Point"].dropna(subset=["name"]).drop_duplicates("name")
    xy = np.column_stack(TO_M.transform(p.geometry.x.to_numpy(), p.geometry.y.to_numpy()))
    names = p["name"].tolist()
    _, idx = cKDTree(xy).query(grid[["x_m", "y_m"]].to_numpy())
    grid["zone"] = [names[i] for i in idx]
    rows = []
    for z, g in grid.groupby("zone"):
        if g.population.sum() < min_pop:
            continue
        pts = [Point(x, y).buffer(141) for x, y in zip(g.x_m, g.y_m)]
        poly = unary_union(pts).buffer(60).buffer(-60)
        rows.append({"zone": z, "population": round(g.population.sum()), "geometry": poly})
    zg = gpd.GeoDataFrame(rows, crs=EPSG)
    grid.loc[~grid.zone.isin(zg.zone), "zone"] = None
    return zg


def coverage_by_zone(grid, stops_ok, radius_m):
    """Partea din populația fiecărui cartier aflată la cel mult radius_m de o stație din stops_ok.
    Folosită doar ca să găsim cartierele cu acces slab; acoperirea din experimente o scrieți voi
    în src/sada/p4/coverage.py."""
    d, _ = cKDTree(stops_ok[["x_m", "y_m"]].to_numpy()).query(grid[["x_m", "y_m"]].to_numpy())
    g = grid.assign(ok=d <= radius_m).dropna(subset=["zone"])
    return g.groupby("zone").apply(lambda z: z.population[z.ok].sum() / z.population.sum(), include_groups=False).to_dict()


def stop_routes(feed, sids, window, min_trips) -> pd.DataFrame:
    """Stațiile fiecărei linii în fereastră, cu intervalul S0 pe sens (mediu pe cele două sensuri)."""
    t = trips_in_window(feed, sids, window[0], window[1])
    w_s = 2 * 3600
    hw = headways(t, window_s=w_s).groupby("route_id").agg(headway_min=("headway_min", "mean"),
                                                            n_trips=("n_trips", "sum"), mode=("mode", "first"),
                                                            route_short_name=("route_short_name", "first"))
    hw = hw[hw.n_trips >= min_trips]
    st = feed["stop_times"]
    st = st[st.trip_id.isin(t[t.route_id.isin(hw.index)].trip_id)].merge(t[["trip_id", "route_id"]], on="trip_id")
    sr = st[["route_id", "stop_id"]].drop_duplicates()
    xy = stops_xy(feed)[["stop_id", "stop_name", "x_m", "y_m", "stop_lat", "stop_lon"]]
    sr = sr.merge(xy, on="stop_id").merge(hw, left_on="route_id", right_index=True)
    return sr


def demand_model(cfg, grid, sr, s0, rng) -> pd.DataFrame:
    """Modelul de cerere, pe linie și fereastră de 15 minute (07:00–09:00).

    1. Generarea: populația fiecărei celule e împărțită între stațiile aflate la ≤ 400 m
       (sau, dacă nu există, la cea mai apropiată stație la ≤ 800 m, cu jumătate de pondere).
    2. Împărțirea pe linii: fiecare stație își împarte pasagerii între liniile care o
       deservesc proporțional cu frecvența lor în S0 (toate liniile urbane, nu doar cele alese).
    3. Încărcarea în secțiunea cea mai încărcată: îmbarcările liniei × min(1, 1,5 × t_c / T_r)
       × κ × un factor de atractivitate a liniei. t_c e durata medie a unei călătorii
       (`dataset.mean_ride_min`), T_r durata unei curse: pe o linie lungă pasagerii coboară pe
       parcurs, deci în secțiunea cea mai încărcată se află doar o parte din cei îmbarcați
       (1,5 = vârful secțiunii față de medie). Apoi un factor de atractivitate (lognormal, σ = σ_a, seed fix: universități, centre comerciale,
       zone industriale pe care populația rezidențială nu le prinde).
    4. Profilul în timp: o curbă de vârf pe cele 8 ferestre, cu vârful decalat pe linie
       (± o fereastră: liniile spre zonele industriale au vârful mai devreme).
    κ se calibrează astfel încât gradul de încărcare mediu al liniilor alese în S0, la
    vârf, să fie `dataset.target_peak_load`. Rezultatul e un MODEL, nu o măsurătoare.
    """
    ds = cfg["dataset"]
    stops = sr.drop_duplicates("stop_id")[["stop_id", "x_m", "y_m"]].reset_index(drop=True)
    tree = cKDTree(stops[["x_m", "y_m"]].to_numpy())
    gen = np.zeros(len(stops))
    for x, y, pop in grid[["x_m", "y_m", "population"]].itertuples(index=False):
        near = tree.query_ball_point((x, y), r=400)
        if near:
            gen[near] += pop / len(near)
        else:
            d, i = tree.query((x, y))
            if d <= 800:
                gen[i] += 0.5 * pop
    stops["gen"] = gen
    freq = sr.assign(f=60 / sr.headway_min)
    freq["share"] = freq.f / freq.groupby("stop_id").f.transform("sum")
    freq = freq.merge(stops[["stop_id", "gen"]], on="stop_id")
    board = (freq.share * freq.gen).groupby(freq.route_id).sum()
    sel = s0.groupby("route_id").agg(n=("n_trips", "mean"), mode=("mode", "first"))
    cap = pd.read_csv(cfg["data"]["capacities"]).set_index("mode")["capacity"]
    attract = pd.Series(np.exp(rng.normal(0, ds["attractiveness_sigma"], len(sel))), index=sel.index)
    dur = pd.read_csv("data/s0_trips.csv").groupby("route_id").duration_s.mean() / 60
    through = np.minimum(1.0, 1.5 * ds["mean_ride_min"] / dur.reindex(sel.index))
    base = board.reindex(sel.index).fillna(0) * through * attract
    shift = pd.Series(rng.integers(-1, 2, len(sel)), index=sel.index)
    prof = np.array(ds["profile"], float)
    offered_peak = sel.n / 8 * sel["mode"].map(cap)            # locuri pe sens, pe fereastră
    peak = base * prof.max()
    kappa = ds["target_peak_load"] * offered_peak.sum() / peak.sum()
    rows = []
    for r in sel.index:
        p = np.roll(prof, shift[r])
        if shift[r] == -1:
            p[-1] = prof[-1]
        elif shift[r] == 1:
            p[0] = prof[0]
        for w in range(8):
            rows.append({"route_id": r, "window": w, "start": f"{7 + w // 4:02d}:{15 * (w % 4):02d}",
                         "passengers": round(float(kappa * base[r] * p[w]), 1)})
    out = pd.DataFrame(rows)
    lf = (out.groupby("route_id").passengers.max() / offered_peak).sort_values()
    print("   gradul de încărcare la vârf în S0, pe linie:", {k: round(v, 2) for k, v in lf.items()})
    return out


def main():
    cfg = load_config("config/default.yaml")
    ds = cfg["dataset"]
    out = Path("data/p4_gtfs")
    out.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = True
    ox.settings.log_console = False
    center = tuple(ds["center"])

    print("1. Capacitățile")
    pd.DataFrame(ds["capacities"]).to_csv(out / "capacitati.csv", index=False)

    print("2. Populația (clădirile OSM, grila de 200 m)")
    grid = population_grid(center, ds["dist_m"], ds["cell_m"], ds["m2_per_person"])

    print("3. Stațiile pe linii (toate liniile urbane din fereastră)")
    feed = load_feed(cfg["gtfs"]["dir"])
    sids = active_service_ids(feed, cfg["gtfs"]["date"])
    sr = stop_routes(feed, sids, cfg["gtfs"]["window"], ds["min_trips_urban"])
    cx, cy = TO_M.transform(center[1], center[0])
    sr = sr[np.hypot(sr.x_m - cx, sr.y_m - cy) <= ds["dist_m"] + 1500]
    sr.to_csv(out / "statii_linii.csv", index=False)
    print(f"   {sr.route_id.nunique()} linii, {sr.stop_id.nunique()} stații")

    print("4. Cartierele și zonele cu acces slab")
    zg = zones(center, ds["dist_m"], grid, ds["zone_min_pop"])
    ok = sr[sr.headway_min <= cfg["controller"]["coverage_headway_min"]].drop_duplicates("stop_id")
    cov = coverage_by_zone(grid, ok, cfg["controller"]["coverage_radius_m"])
    zg["coverage_s0"] = zg.zone.map(cov).round(3)
    zg = zg.to_crs(4326)
    zg.to_file(out / "zone.geojson", driver="GeoJSON")
    weak = zg.sort_values("coverage_s0").head(ds["n_weak_zones"])
    weak.to_file(out / "zone_acces_slab.geojson", driver="GeoJSON")
    print(f"   {len(zg)} cartiere; cu acces slab: " +
          ", ".join(f"{z} ({c:.0%})" for z, c in zip(weak.zone, weak.coverage_s0)))
    grid.to_csv(out / "populatie_grila.csv", index=False)

    print("5. Modelul de cerere -> încărcări")
    s0 = pd.read_csv(cfg["data"]["s0"])
    loads = demand_model(cfg, grid, sr, s0, np.random.default_rng(ds["seed"]))
    loads.to_csv(out / "incarcari.csv", index=False)
    print(f"Salvat în {out}/.")


if __name__ == "__main__":
    main()
