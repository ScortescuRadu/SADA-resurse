"""Timpul de întoarcere la capăt măsurat din GTFS, în loc de cele 5 minute presupuse în kit.

Feed-ul STPT are block_id în trips.txt: cursele consecutive ale aceluiași vehicul. Diferența
dintre plecarea următoarei curse și sosirea celei curente e timpul petrecut la capăt. Pe
liniile din Timișoara iese între 1 și 10 minute (mediana pe rețea 6), deci 5 minute peste tot
subestimează unele linii și le supraestimează pe altele.

    from sada.p4.layover import measured_layover
    lay = measured_layover(feed, sids, "07:00:00", "09:00:00", route_ids)   # {route_id: minute}

Ca să-l folosiți în S0, modificați în baseline.vehicle_hours înmulțirea cu layover_min astfel
încât să accepte și un dicționar pe linie (o linie de cod), apoi în scripts/baseline_s0.py
dați rezultatul lui measured_layover în loc de numărul din config.
"""
from __future__ import annotations

from .baseline import _hms, trips_in_window


def measured_layover(feed: dict, service_ids, start, end, route_ids=None, max_gap_min: float = 60.0,
                     default: float = 5.0) -> dict:
    """Mediana pe linie a timpului dintre două curse consecutive ale aceluiași vehicul, pentru
    cursele care pleacă în fereastră. Golurile mai lungi de max_gap_min (vehiculul a mers la
    depou) nu se numără. Liniile fără date primesc `default`."""
    if "block_id" not in feed["trips"] or feed["trips"]["block_id"].isna().all():
        return {}
    t0, t1 = _hms(start), _hms(end)
    t = trips_in_window(feed, service_ids, t0 - 3 * 3600, t1 + 3 * 3600, route_ids)
    t = t.merge(feed["trips"][["trip_id", "block_id"]], on="trip_id").sort_values(["block_id", "dep_s"])
    t["gap_min"] = (t.groupby("block_id")["dep_s"].shift(-1) - t["arr_s"]) / 60.0
    w = t[(t["dep_s"] >= t0) & (t["dep_s"] < t1) & t["gap_min"].between(0, max_gap_min)]
    med = w.groupby("route_id")["gap_min"].median().to_dict()
    ids = route_ids if route_ids is not None else t["route_id"].unique()
    return {r: float(med.get(r, default)) for r in map(str, ids)}
