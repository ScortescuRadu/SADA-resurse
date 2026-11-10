"""Acoperirea: ponderea populației la cel mult 400 m de o stație cu interval de
cel mult 20 de minute. TODO (GHID.md, pasul 6). Proiecția stațiilor în metri e
gata: gtfs_io.stops_xy(feed).

Sugestie: scipy.spatial.cKDTree pe coordonatele (x_m, y_m) ale stațiilor bine
deservite, apoi tree.query_ball_point(punctele_populației, r=400).
"""
from __future__ import annotations


def coverage_share(population_points, stops_ok_xy, radius_m: float = 400.0) -> float:
    """population_points: DataFrame cu x_m, y_m, population. stops_ok_xy: stațiile
    cu interval ≤ 20 min, cu x_m, y_m. Întoarce ponderea populației acoperite. TODO"""
    raise NotImplementedError("coverage_share (GHID.md, pasul 6)")
