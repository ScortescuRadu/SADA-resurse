"""Controllerul MAPE-K pentru coridor. TODO (GHID.md, pasul 6).

Model de pornire: examples/toy_mapek.py (are deja histerezis).
"""
from __future__ import annotations

from sada.mapek import Controller

REGIMES = ("liber", "aglomerat", "blocat")


class TrafficController(Controller):
    """M: densitate și viteză pe tronsoane, la fiecare `window_s` secunde.
    A: regimul fiecărui tronson, cu praguri cu histerezis din config["controller"].
    P: regula (sau parametrii p, vmax) pentru fiecare tronson, în fereastra următoare.
    E: corridor.set_rule(...), fără oprirea simulării.
    K: regimul anterior pe tronsoane, jurnalul schimbărilor.
    """

    def monitor(self, corridor, t):
        raise NotImplementedError

    def analyze(self, measurements, t):
        raise NotImplementedError

    def plan(self, regimes, t):
        raise NotImplementedError

    def execute(self, corridor, action, t):
        raise NotImplementedError
