"""Calculează orarul de referință S0 pentru liniile alese (GHID.md, pasul 2):
curse, interval mediu și ore-vehicul pe linie, în fereastra de vârf.

    python scripts/baseline_s0.py

Liniile se aleg în config (gtfs.routes, după route_short_name). Rezultatul:
data/s0.csv (pe linie) și data/s0_trips.csv (pe cursă).
"""
from __future__ import annotations

from pathlib import Path

from sada.config import load_config
from sada.p4.baseline import headways, trips_in_window, vehicle_hours
from sada.p4.gtfs_io import active_service_ids, load_feed


def main():
    cfg = load_config("config/default.yaml")
    g = cfg["gtfs"]
    feed = load_feed(g["dir"])
    sids = active_service_ids(feed, g["date"])
    if not sids:
        raise SystemExit(f"Niciun serviciu activ pe {g['date']}. Rulați scripts/inspect_gtfs.py.")
    routes = feed["routes"]
    wanted = [str(x) for x in g.get("routes") or []]
    if wanted:
        sel = routes[routes["route_short_name"].isin(wanted)]
        missing = set(wanted) - set(sel["route_short_name"])
        if missing:
            print(f"ATENȚIE: nu găsesc liniile {sorted(missing)} în routes.txt")
        route_ids = sel["route_id"].tolist()
    else:
        route_ids = None
        print("gtfs.routes e gol în config: calculez pentru toate liniile.")
    t = trips_in_window(feed, sids, g["window"][0], g["window"][1], route_ids)
    w_s = (sum(int(x) * f for x, f in zip(g["window"][1].split(":"), (3600, 60, 1)))
           - sum(int(x) * f for x, f in zip(g["window"][0].split(":"), (3600, 60, 1))))
    hw = headways(t, window_s=w_s)
    vh = vehicle_hours(t, layover_min=g["layover_min"])
    s0 = hw.merge(vh[["route_id", "vehicle_hours"]], on="route_id", how="left")
    Path("data").mkdir(exist_ok=True)
    s0.to_csv(cfg["data"]["s0"], index=False)
    t.to_csv("data/s0_trips.csv", index=False)
    print(s0.to_string(index=False))
    print(f"\nTotal ore-vehicul în fereastra {g['window'][0]}–{g['window'][1]}: {vh['vehicle_hours'].sum():.1f} "
          f"(layover {g['layover_min']} min/cursă). Salvat {cfg['data']['s0']}")
    modes = set(s0["mode"])
    for m in ("tramvai", "troleibuz", "autobuz"):
        if m not in modes:
            print(f"ATENȚIE: fișa cere cel puțin o linie de {m}; nu am găsit niciuna în selecție.")


if __name__ == "__main__":
    main()
