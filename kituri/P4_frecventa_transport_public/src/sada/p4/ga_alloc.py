"""Alocarea curselor pe linii cu un algoritm genetic. TODO (GHID.md, pasul 5).

Individ: vector întreg, numărul de curse pe fiecare linie în fereastra următoare.
Constrângere: Σ curse_i × ore_vehicul_per_cursă_i ≤ totalul din S0 (flota).
Fitness: de exemplu, −(penalizare_mare × pasageri în curse supraaglomerate
         + timpul mediu de așteptare ponderat cu pasagerii).
Reparare: dacă depășește bugetul, scădeți curse de pe liniile cu cel mai mic câștig.
Limite: cel puțin atâtea curse cât să nu depășiți max_headway_min pe nicio linie.
"""
from __future__ import annotations


def allocate(state: dict, cfg: dict, rng) -> dict:
    """Întoarce {route_id: număr_de_curse} pentru fereastra următoare. TODO"""
    raise NotImplementedError("ga_alloc.allocate (GHID.md, pasul 5)")
