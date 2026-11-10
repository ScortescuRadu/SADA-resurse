"""Citirea unui feed GTFS cu pandas și câteva funcții de bază.

    feed = load_feed("data/raw/gtfs")             # folder dezarhivat sau .zip
    sids = active_service_ids(feed, "2026-10-14") # o zi lucrătoare
    trips = feed["trips"][feed["trips"].service_id.isin(sids)]

Toate coloanele se citesc ca text, ca să nu se piardă zerourile din față ale
ID-urilor. Orele din stop_times pot depăși 24:00:00 (curse după miezul nopții);
folosiți time_to_seconds, nu conversia în datetime.
"""
from __future__ import annotations

import datetime as dt
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

FILES = ["agency", "stops", "routes", "trips", "stop_times", "calendar", "calendar_dates", "shapes", "frequencies"]

# tipurile de bază GTFS și cele extinse (Google „extended route types”) folosite des în Europa
ROUTE_TYPES = {0: "tramvai", 1: "metrou", 2: "tren", 3: "autobuz", 4: "feribot", 11: "troleibuz",
               700: "autobuz", 704: "autobuz", 800: "troleibuz", 900: "tramvai"}


def load_feed(path: str | Path) -> dict[str, pd.DataFrame]:
    path = Path(path)
    feed = {}
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            names = {Path(n).name: n for n in z.namelist()}
            for f in FILES:
                if f"{f}.txt" in names:
                    feed[f] = pd.read_csv(io.BytesIO(z.read(names[f"{f}.txt"])), dtype=str, encoding="utf-8-sig")
    else:
        for f in FILES:
            p = path / f"{f}.txt"
            if p.exists():
                feed[f] = pd.read_csv(p, dtype=str, encoding="utf-8-sig")
    missing = [f for f in ("stops", "routes", "trips", "stop_times") if f not in feed]
    if missing:
        raise FileNotFoundError(f"Lipsesc fișierele GTFS obligatorii: {missing}")
    for df in feed.values():
        df.columns = [c.strip() for c in df.columns]
    return feed


def time_to_seconds(s: pd.Series) -> pd.Series:
    """'25:10:00' -> 90600. Valorile lipsă rămân NaN."""
    parts = s.str.strip().str.split(":", expand=True)
    return parts[0].astype(float) * 3600 + parts[1].astype(float) * 60 + parts[2].astype(float)


def route_mode(route_type) -> str:
    try:
        return ROUTE_TYPES.get(int(route_type), f"tip {route_type}")
    except (TypeError, ValueError):
        return "necunoscut"


def active_service_ids(feed: dict, date: str | dt.date) -> set[str]:
    """Serviciile active într-o zi: calendar.txt (zi a săptămânii + interval)
    corectat cu excepțiile din calendar_dates.txt (1 = adăugat, 2 = scos)."""
    d = pd.Timestamp(date).date()
    ymd = d.strftime("%Y%m%d")
    active = set()
    if "calendar" in feed:
        cal = feed["calendar"]
        day = d.strftime("%A").lower()
        m = (cal[day] == "1") & (cal["start_date"] <= ymd) & (cal["end_date"] >= ymd)
        active |= set(cal.loc[m, "service_id"])
    if "calendar_dates" in feed:
        cd = feed["calendar_dates"]
        cd = cd[cd["date"] == ymd]
        active |= set(cd.loc[cd["exception_type"] == "1", "service_id"])
        active -= set(cd.loc[cd["exception_type"] == "2", "service_id"])
    return active


def feed_date_range(feed: dict) -> tuple[str, str] | None:
    if "calendar" in feed and len(feed["calendar"]):
        return feed["calendar"]["start_date"].min(), feed["calendar"]["end_date"].max()
    if "calendar_dates" in feed and len(feed["calendar_dates"]):
        return feed["calendar_dates"]["date"].min(), feed["calendar_dates"]["date"].max()
    return None


def stops_xy(feed: dict, epsg: int = 3844) -> pd.DataFrame:
    """Coordonatele stațiilor proiectate în metri (implicit Stereo 70, EPSG:3844),
    ca distanțele să se poată calcula direct. Coloane noi: x_m, y_m."""
    from pyproj import Transformer
    st = feed["stops"].copy()
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    x, y = tr.transform(st["stop_lon"].astype(float).to_numpy(), st["stop_lat"].astype(float).to_numpy())
    st["x_m"], st["y_m"] = np.asarray(x), np.asarray(y)
    return st
