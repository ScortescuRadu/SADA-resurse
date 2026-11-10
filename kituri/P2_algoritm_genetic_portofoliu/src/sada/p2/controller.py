"""Controllerul MAPE-K pentru algoritmul genetic dinamic. TODO (GHID.md, pasul 6).

Mecanismul de detecție recomandat: indivizi de control (santinele). Se aleg
câțiva indivizi fixați și se reevaluează la fiecare generație. Dacă fitness-ul lor
se schimbă deși ei nu s-au schimbat, problema s-a modificat.
"""
from __future__ import annotations

import numpy as np

from sada.mapek import Controller


class DynamicGAController(Controller):
    """M: cel mai bun, media, diversitatea; fitness-ul santinelelor (reevaluate).
    A: „schimbare detectată” / „stagnare” / „normal”.
    P: răspunsul ales din config["controller"]["response"]: hipermutație,
       imigranți aleatori sau repornire parțială (păstrând arhiva).
    E: modifică ga.p_mut, apelează ga.replace_random(...) etc.
    K: santinelele și fitness-ul lor anterior, arhiva soluțiilor bune,
       generația de la care a început hipermutația, jurnalul.
    """

    def monitor(self, ga, g):
        # Sugestie: la prima apelare alegeți santinelele (de ex. 5 indivizi aleatori
        # din populația inițială) și păstrați-le în self.k.state["sentinels"].
        # Reevaluarea lor costă evaluări: adunați-le la ga.evaluations.
        raise NotImplementedError

    def analyze(self, m, g):
        raise NotImplementedError

    def plan(self, assessment, g):
        raise NotImplementedError

    def execute(self, ga, action, g):
        raise NotImplementedError


def sentinel_changed(old: np.ndarray, new: np.ndarray, rel_tol: float = 1e-9) -> bool:
    """Adevărat dacă fitness-ul vreunei santinele s-a schimbat (gata de folosit)."""
    return bool(np.any(np.abs(new - old) > rel_tol * np.maximum(1.0, np.abs(old))))
