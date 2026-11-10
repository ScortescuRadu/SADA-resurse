"""Modelul Nagel–Schreckenberg (NaSch) pe un inel cu o singură bandă.

Acesta e primul lucru de implementat (GHID.md, pasul 1). Infrastructura e
gata: inițializarea, calculul distanțelor, măsurătorile. Voi completați
`RingRoad.step`, adică cele patru reguli și variantele VDR și slow-to-start.

Convenții:
  - pozițiile sunt indici de celule 0..L-1, vitezele sunt în celule/pas;
  - `self.pos` e mereu sortat crescător, iar `self.vel[i]` e viteza vehiculului
    de la `self.pos[i]`; vehiculul din fața lui i este i+1 (cu ocolire la capăt);
  - inelul are condiții la limită periodice: ce iese în dreapta intră în stânga.
"""
from __future__ import annotations

import numpy as np

RULES = ("nasch", "vdr", "sts")


class RingRoad:
    def __init__(self, length: int = 1000, density: float = 0.2, vmax: int = 2, p: float = 0.3,
                 p0: float | None = None, rule: str = "nasch", rng: np.random.Generator | None = None):
        if rule not in RULES:
            raise ValueError(f"rule trebuie să fie una dintre {RULES}")
        self.rng = rng if rng is not None else np.random.default_rng()
        self.L = int(length)
        self.vmax, self.p, self.rule = int(vmax), float(p), rule
        self.p0 = float(p0) if p0 is not None else float(p)   # folosit de VDR
        n = max(1, int(round(density * self.L)))
        self.pos = np.sort(self.rng.choice(self.L, size=n, replace=False))
        self.vel = np.zeros(n, dtype=int)
        # pentru slow-to-start: vehiculele blocate la pasul anterior (v = 0 și gap = 0)
        self.blocked_before = np.zeros(n, dtype=bool)
        self.t = 0

    # ------------------------------------------------------------ ajutoare
    @property
    def n(self) -> int:
        return len(self.pos)

    def gaps(self) -> np.ndarray:
        """Numărul de celule libere până la vehiculul din față, pentru fiecare vehicul."""
        if self.n == 1:
            return np.array([self.L - 1])
        ahead = np.roll(self.pos, -1)
        return (ahead - self.pos - 1) % self.L

    def occupancy(self) -> np.ndarray:
        """Un rând al diagramei spațiu-timp: -1 pentru celulă goală, altfel viteza."""
        row = np.full(self.L, -1, dtype=int)
        row[self.pos] = self.vel
        return row

    @property
    def density(self) -> float:
        return self.n / self.L

    @property
    def mean_speed(self) -> float:
        return float(self.vel.mean())

    @property
    def flow(self) -> float:
        """Flux = densitate × viteză medie [vehicule/celulă/pas × celule/pas]."""
        return self.density * self.mean_speed

    # ------------------------------------------------------------ dinamica
    def step(self) -> None:
        """Un pas de timp, cu actualizare PARALELĂ (toate vehiculele deodată).

        TODO (GHID.md, pașii 1 și 4):
          1. accelerare:           v <- min(v + 1, vmax)
             la "sts": un vehicul care la pasul anterior era blocat (v = 0 și
             gap = 0, adică self.blocked_before) și acum are loc în față mai
             așteaptă un pas (rămâne la 0); abia la pasul următor pornește
          2. frânare:              v <- min(v, gap)          (gap = self.gaps())
          3. încetinire aleatoare: cu probabilitatea p, v <- max(v - 1, 0)
             la "vdr": vehiculele cu v = 0 la începutul pasului folosesc p0 în loc de p
          4. deplasare:            pos <- (pos + v) mod L
        La final: actualizați self.blocked_before (v == 0 și gap == 0 la acest pas,
        înainte de deplasare), reordonați pos, vel și blocked_before împreună
        (np.argsort) și incrementați self.t.

        Folosiți self.rng pentru numerele aleatoare, ca rezultatele să depindă doar de seed.
        """
        raise NotImplementedError("RingRoad.step (GHID.md, pasul 1)")
