"""Prima privire asupra feed-ului (GHID.md, pasul 1): operatori, linii pe tip,
servicii, perioada de valabilitate, câte curse are o zi lucrătoare.

    python scripts/inspect_gtfs.py
    python scripts/inspect_gtfs.py --date 2026-10-14
"""
from __future__ import annotations

import argparse

from sada.config import load_config
from sada.p4.gtfs_io import active_service_ids, feed_date_range, load_feed, route_mode


def main():
    cfg = load_config("config/default.yaml")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=cfg["gtfs"]["dir"])
    ap.add_argument("--date", default=cfg["gtfs"]["date"])
    a = ap.parse_args()
    feed = load_feed(a.dir)

    if "agency" in feed:
        print("Operatori:", ", ".join(feed["agency"]["agency_name"].tolist()))
    print("Perioada:", feed_date_range(feed))
    r = feed["routes"].copy()
    r["mod"] = r["route_type"].map(route_mode)
    print("\nLinii pe tip (route_type -> mod):")
    print(r.groupby(["route_type", "mod"]).size().to_string())
    sids = active_service_ids(feed, a.date)
    print(f"\nServicii active pe {a.date}: {sorted(sids)}")
    trips = feed["trips"][feed["trips"]["service_id"].isin(sids)]
    print(f"Curse în ziua aceea: {len(trips)}")
    per = trips.merge(r[["route_id", "route_short_name", "mod"]], on="route_id") \
               .groupby(["mod", "route_short_name"]).size().rename("curse").reset_index()
    print("\nCurse pe linie (primele 40):")
    print(per.sort_values(["mod", "route_short_name"]).head(40).to_string(index=False))
    if not sids:
        print("\nATENȚIE: niciun serviciu activ în data aleasă. Alegeți o zi lucrătoare din perioada de mai sus.")


if __name__ == "__main__":
    main()
