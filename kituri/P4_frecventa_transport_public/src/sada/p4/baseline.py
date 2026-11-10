"""Orarul de referință S0: cursele dintr-o fereastră, intervalele, orele-vehicul.

    trips = trips_in_window(feed, sids, "07:00:00", "09:00:00", route_ids=[...])
    hw = headways(trips)                     # interval mediu pe linie și sens
    vh = vehicle_hours(trips, layover_min=5)  # ore-vehicul pe linie
"""
from __future__ import annotations

import pandas as pd

from .gtfs_io import route_mode, time_to_seconds


def _hms(t) -> float:
    return float(time_to_seconds(pd.Series([t])).iloc[0]) if isinstance(t, str) else float(t)


def trips_in_window(feed: dict, service_ids, start, end, route_ids=None) -> pd.DataFrame:
    """Cursele care PLEACĂ din capăt în [start, end). Pentru fiecare: plecarea,
    sosirea la ultima stație și durata, în secunde de la începutul zilei."""
    t0, t1 = _hms(start), _hms(end)
    trips = feed["trips"]
    trips = trips[trips["service_id"].isin(set(service_ids))]
    if route_ids is not None:
        trips = trips[trips["route_id"].isin(set(map(str, route_ids)))]
    st = feed["stop_times"]
    st = st[st["trip_id"].isin(set(trips["trip_id"]))].copy()
    st["seq"] = st["stop_sequence"].astype(int)
    st["dep_s"] = time_to_seconds(st["departure_time"].fillna(st["arrival_time"]))
    st["arr_s"] = time_to_seconds(st["arrival_time"].fillna(st["departure_time"]))
    st = st.sort_values(["trip_id", "seq"])
    first = st.groupby("trip_id").first()[["dep_s", "stop_id"]].rename(columns={"stop_id": "first_stop"})
    last = st.groupby("trip_id").last()[["arr_s", "stop_id"]].rename(columns={"stop_id": "last_stop"})
    out = trips.set_index("trip_id").join(first).join(last).reset_index()
    if "direction_id" not in out:
        out["direction_id"] = "0"
    out["direction_id"] = out["direction_id"].fillna("0")
    out["duration_s"] = out["arr_s"] - out["dep_s"]
    out = out[(out["dep_s"] >= t0) & (out["dep_s"] < t1)]
    routes = feed["routes"].set_index("route_id")
    out["route_short_name"] = out["route_id"].map(routes.get("route_short_name", pd.Series(dtype=str)))
    out["mode"] = out["route_id"].map(routes["route_type"]).map(route_mode)
    cols = ["trip_id", "route_id", "route_short_name", "mode", "direction_id", "service_id",
            "dep_s", "arr_s", "duration_s", "first_stop", "last_stop"]
    return out[cols].sort_values(["route_id", "direction_id", "dep_s"]).reset_index(drop=True)


def headways(trips: pd.DataFrame, window_s: float | None = None) -> pd.DataFrame:
    """Intervalul mediu de succedare pe linie și sens, în minute. Dacă dați durata
    ferestrei, intervalul se calculează ca fereastră / număr de curse (mai robust
    când sunt puține curse); altfel, media diferențelor dintre plecări."""
    rows = []
    for (r, d), g in trips.groupby(["route_id", "direction_id"]):
        n = len(g)
        if window_s:
            hw = window_s / n / 60.0
        else:
            hw = g["dep_s"].sort_values().diff().dropna().mean() / 60.0 if n > 1 else float("nan")
        rows.append({"route_id": r, "direction_id": d, "route_short_name": g["route_short_name"].iloc[0],
                     "mode": g["mode"].iloc[0], "n_trips": n, "headway_min": hw})
    return pd.DataFrame(rows)


def vehicle_hours(trips: pd.DataFrame, layover_min: float = 5.0) -> pd.DataFrame:
    """Orele-vehicul pe linie: suma duratelor curselor + un timp de întoarcere la
    capăt (layover) pe cursă. Layover-ul e o ipoteză; spuneți ce valoare ați folosit."""
    g = trips.groupby("route_id").agg(n_trips=("trip_id", "size"), drive_s=("duration_s", "sum"),
                                      route_short_name=("route_short_name", "first"), mode=("mode", "first"))
    g["vehicle_hours"] = (g["drive_s"] + g["n_trips"] * layover_min * 60) / 3600.0
    return g.reset_index()
