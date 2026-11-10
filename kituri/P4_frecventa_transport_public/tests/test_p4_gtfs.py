"""Teste pentru citirea GTFS și orarul de referință, pe un feed minuscul de test
(tests/fixtures/mini_gtfs). Rulare: pytest -q"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sada.p4.baseline import headways, trips_in_window, vehicle_hours
from sada.p4.gtfs_io import active_service_ids, load_feed, route_mode, stops_xy, time_to_seconds

FIX = Path(__file__).parent / "fixtures" / "mini_gtfs"


@pytest.fixture
def feed():
    return load_feed(FIX)


def test_times_after_midnight():
    s = time_to_seconds(pd.Series(["07:00:00", "25:10:00", " 8:05:30"]))
    assert s.tolist() == [25200, 90600, 29130]


def test_service_ids_weekday_weekend_and_exceptions(feed):
    assert active_service_ids(feed, "2026-10-14") == {"LV"}          # miercuri
    assert active_service_ids(feed, "2026-10-17") == {"SD"}          # sâmbătă
    assert active_service_ids(feed, "2026-12-01") == {"SD"}          # zi liberă: excepții


def test_trips_in_window(feed):
    t = trips_in_window(feed, {"LV"}, "07:00:00", "09:00:00")
    assert set(t.trip_id) == {"T2", "T3", "T4", "T5", "T6", "T7"}    # T1 pleacă 06:50, T9 după miezul nopții
    assert t.set_index("trip_id").loc["T7", "duration_s"] == 40 * 60
    assert t.set_index("trip_id").loc["T2", "mode"] == "tramvai"


def test_headways_and_vehicle_hours(feed):
    t = trips_in_window(feed, {"LV"}, "07:00:00", "09:00:00")
    hw = headways(t).set_index("route_id")
    assert np.isclose(hw.loc["R1", "headway_min"], 30.0)
    hw2 = headways(t, window_s=7200).set_index("route_id")
    assert np.isclose(hw2.loc["R1", "headway_min"], 40.0)
    vh = vehicle_hours(t, layover_min=0).set_index("route_id")
    assert np.isclose(vh.loc["R1", "vehicle_hours"], 1.0)


def test_route_modes():
    assert route_mode("11") == "troleibuz" and route_mode(900) == "tramvai" and route_mode("3") == "autobuz"


def test_stops_projection(feed):
    st = stops_xy(feed)
    d = np.hypot(*(st.loc[0, ["x_m", "y_m"]].to_numpy(float) - st.loc[1, ["x_m", "y_m"]].to_numpy(float)))
    assert 700 < d < 1000      # Capăt Nord - Centru, aproximativ 850 m
