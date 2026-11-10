"""Descarcă rețeaua rutieră din OpenStreetMap cu OSMnx și o salvează ca GraphML.
Pachetul disciplinei conține deja graful (p3_retea/); folosiți scriptul dacă
vreți să înțelegeți cum s-a obținut sau să lucrați pe altă zonă.

    python scripts/download_graph.py                          # parametrii din config (osm:)
    python scripts/download_graph.py --lat 45.7537 --lon 21.2257 --dist 1500

Fișa cere un graf de 500–3000 de noduri. Dacă iese mai mare, micșorați --dist
sau măriți --tolerance (unirea intersecțiilor apropiate).

Datele OSM: © OpenStreetMap contributors, licența ODbL.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import osmnx as ox

from sada.config import load_config


def main():
    cfg = load_config("config/default.yaml")["osm"]
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=cfg["center"][0])
    ap.add_argument("--lon", type=float, default=cfg["center"][1])
    ap.add_argument("--dist", type=float, default=cfg["dist_m"], help="raza [m]")
    ap.add_argument("--network-type", default=cfg.get("network_type", "drive"))
    ap.add_argument("--tolerance", type=float, default=cfg.get("consolidate_tolerance_m", 15),
                    help="unește intersecțiile mai apropiate de atât [m]; 0 = fără")
    ap.add_argument("--out", default=cfg["out"])
    a = ap.parse_args()

    ox.settings.use_cache = True
    ox.settings.log_console = False
    print(f"Descarc rețeaua '{a.network_type}' în jurul ({a.lat}, {a.lon}), raza {a.dist:.0f} m ...")
    G = ox.graph_from_point((a.lat, a.lon), dist=a.dist, network_type=a.network_type, simplify=True)
    print(f"  brut: {G.number_of_nodes()} noduri, {G.number_of_edges()} muchii")

    if a.tolerance > 0:
        Gp = ox.project_graph(G)
        Gp = ox.consolidate_intersections(Gp, tolerance=a.tolerance, rebuild_graph=True, dead_ends=False)
        G = ox.project_graph(Gp, to_latlong=True)
        print(f"  după unirea intersecțiilor (toleranță {a.tolerance:.0f} m): {G.number_of_nodes()} noduri")

    G = ox.truncate.largest_component(G, strongly=True)
    G = ox.routing.add_edge_speeds(G)
    G = ox.routing.add_edge_travel_times(G)
    n = G.number_of_nodes()
    print(f"  componenta tare conexă cea mai mare: {n} noduri, {G.number_of_edges()} muchii")
    if not 500 <= n <= 3000:
        print("  ATENȚIE: fișa cere 500–3000 de noduri; ajustați --dist sau --tolerance.")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(G, out)
    print(f"Salvat {out}")
    print(f"Pentru data/DATA.md: OpenStreetMap prin OSMnx, centru=({a.lat}, {a.lon}), raza={a.dist:.0f} m, "
          f"{dt.date.today().isoformat()}, ODbL")


if __name__ == "__main__":
    main()
