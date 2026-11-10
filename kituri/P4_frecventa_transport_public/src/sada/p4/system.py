"""Starea sistemului de transport pe care o gestionează controllerul.

Totul se socotește pe ferestre de 15 minute:
  trips[r]        curse ale liniei r în fereastra curentă (pot fi fracționare în model)
  vh_per_trip[r]  ore-vehicul consumate de o cursă (durata + întoarcerea la capăt)
  capacity[r]     locuri într-un vehicul al liniei r
  demand[(r, w)]  pasageri ai liniei r în fereastra w (din tabelul de încărcări)

Bugetul de flotă este numărul de ore-vehicul pe fereastră din orarul S0 și
rămâne constant. Gata de folosit, cu excepția `from_files`, care depinde de
formatul fișierelor din pachet (GHID.md, pasul 3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class TransitSystem:
    routes: list
    trips: dict
    vh_per_trip: dict
    capacity: dict
    demand: dict
    window_min: int = 15
    budget_vh: float | None = None
    window: int = 0
    closed: set = field(default_factory=set)
    demand_factor: dict = field(default_factory=dict)     # perturbări: linie -> factor

    def __post_init__(self):
        if self.budget_vh is None:
            self.budget_vh = self.used_vehicle_hours()

    # ------------------------------------------------------------ măsurători
    def used_vehicle_hours(self) -> float:
        return float(sum(self.trips[r] * self.vh_per_trip[r] for r in self.routes))

    def headway_min(self, r) -> float:
        return self.window_min / self.trips[r] if self.trips[r] > 0 else math.inf

    def passengers(self, r, w: int | None = None) -> float:
        w = self.window if w is None else w
        return float(self.demand.get((r, w), 0.0)) * self.demand_factor.get(r, 1.0)

    def load_factor(self, r, w: int | None = None) -> float:
        offered = self.trips[r] * self.capacity[r]
        pax = self.passengers(r, w)
        return pax / offered if offered > 0 else (math.inf if pax > 0 else 0.0)

    def mean_wait_min(self, w: int | None = None) -> float:
        """Timpul mediu de așteptare (jumătate din interval), ponderat cu pasagerii."""
        tot = sum(self.passengers(r, w) for r in self.routes if r not in self.closed)
        if tot == 0:
            return 0.0
        return sum(self.passengers(r, w) * self.headway_min(r) / 2 for r in self.routes
                   if r not in self.closed and self.trips[r] > 0) / tot

    # ------------------------------------------------------------ acțiuni
    def move_trip(self, src, dst, n: float = 1.0) -> None:
        """Mută n curse de pe src pe dst, convertind prin ore-vehicul (bugetul rămâne același)."""
        vh = n * self.vh_per_trip[src]
        self.trips[src] -= n
        self.trips[dst] += vh / self.vh_per_trip[dst]

    def close_route(self, r, release_vehicles: bool) -> None:
        """Scoate linia din circulație. Dacă release_vehicles, bugetul rămâne același (vehiculele
        pot fi folosite pe alte linii); altfel bugetul scade cu orele-vehicul ale liniei."""
        if not release_vehicles:
            self.budget_vh -= self.trips[r] * self.vh_per_trip[r]
        self.trips[r] = 0.0
        self.closed.add(r)

    def advance(self) -> None:
        self.window += 1

    # ------------------------------------------------------------ construire
    @classmethod
    def from_files(cls, cfg: dict) -> "TransitSystem":
        """TODO (GHID.md, pasul 3): construiți sistemul din data/s0.csv, tabelul de
        încărcări și capacitățile din pachet. Cereți curse pe fereastră:
        trips[r] = n_trips_în_S0 * 15 / durata_ferestrei_în_minute."""
        raise NotImplementedError("TransitSystem.from_files (GHID.md, pasul 3)")
