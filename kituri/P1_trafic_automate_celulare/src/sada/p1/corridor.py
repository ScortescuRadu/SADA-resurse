"""Coridorul urban: 2-3 benzi, intrare și ieșire deschise, tronsoane de măsurare.

TODO (GHID.md, pasul 5). Structura de mai jos e o sugestie; o puteți schimba.

Ce trebuie să știe să facă:
  - să injecteze vehicule la intrare după un debit [veh/h] (proces Poisson pe pas);
  - să aplice regula curentă *a fiecărui tronson* (regula poate diferi pe tronsoane);
  - să schimbe banda după o regulă simplă (blocat în față, loc pe banda vecină);
  - să scoată vehiculele la ieșire și să le rețină timpul de parcurs;
  - să blocheze temporar o celulă pe o bandă (incidentul);
  - să întoarcă măsurători pe tronsoane (densitate, viteză medie) pentru controller.
"""
from __future__ import annotations

import numpy as np


class Corridor:
    def __init__(self, cfg: dict, inflow_veh_h: float, rng: np.random.Generator):
        m = cfg["model"]
        self.rng = rng
        self.lanes = int(m["lanes"])
        self.cells = int(round(m["length_m"] / m["cell_m"]))
        self.segment_cells = int(round(m["segment_m"] / m["cell_m"]))
        self.n_segments = int(np.ceil(self.cells / self.segment_cells))
        self.vmax, self.p, self.p0 = m["vmax"], m["p"], m["p0"]
        self.dt = m["dt_s"]
        self.inflow_per_step = inflow_veh_h / 3600.0 * self.dt
        # regula pe fiecare tronson; controllerul o schimbă prin set_rule
        self.segment_rule = ["nasch"] * self.n_segments
        self.t = 0
        self.travel_times: list[float] = []   # completat la ieșirea vehiculelor
        self.exit_count = 0
        # TODO: structura de date pentru vehicule (de ex. matrice benzi × celule cu
        #       viteze și -1 pentru celule goale, plus timpul de intrare al fiecărui vehicul)

    def set_rule(self, segment: int, rule: str) -> None:
        self.segment_rule[segment] = rule

    def block(self, lane: int, cell: int, active: bool) -> None:
        """Incidentul: o celulă blocată (un vehicul oprit) pe o bandă."""
        raise NotImplementedError("Corridor.block (GHID.md, pasul 8)")

    def step(self) -> None:
        raise NotImplementedError("Corridor.step (GHID.md, pasul 5)")

    def segment_measurements(self) -> dict:
        """{"density_veh_km": vector pe tronsoane, "speed_km_h": vector pe tronsoane}"""
        raise NotImplementedError("Corridor.segment_measurements (GHID.md, pasul 6)")
