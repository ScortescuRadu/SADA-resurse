"""Controllerele pentru frecvență. TODO (GHID.md, pașii 4–5).

Ambele lucrează pe ferestre de 15 minute simulate, primesc un
`sada.p4.system.TransitSystem` și păstrează constant totalul de ore-vehicul
(folosiți system.move_trip, care convertește prin ore-vehicul). Diferă doar în
etapa P (cum calculează noua alocare).
"""
from __future__ import annotations

from sada.mapek import Controller


class SimpleRuleController(Controller):
    """P: mută o cursă de pe linia cea mai puțin încărcată pe cea mai încărcată,
    respectând intervalul maxim (config: max_headway_min)."""

    def monitor(self, system, t):
        raise NotImplementedError

    def analyze(self, m, t):
        raise NotImplementedError

    def plan(self, assessment, t):
        raise NotImplementedError

    def execute(self, system, action, t):
        raise NotImplementedError


class GAController(SimpleRuleController):
    """La fel ca SimpleRuleController, dar P rulează un algoritm genetic care
    caută alocarea întreagă de curse pe linii (vedeți ga_alloc.py)."""

    def plan(self, assessment, t):
        raise NotImplementedError
