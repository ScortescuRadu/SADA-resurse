"""Problema portofoliului: citire, obiectiv, fezabilitate, schimbări în timpul rulării.

Două tipuri de probleme:
  - "binary"  (ramurile A și C): x[i] ∈ {0, 1}, 1 = intervenția e finanțată;
  - "integer" (ramura B): x[i] = orele-vehicul alocate liniei i, între lower[i] și upper[i].

Formatul fișierelor JSON e cel produs de scripts/prepare_data.py (instanțe de
dezvoltare). Dacă fișierele din pachetul disciplinei au alt format, adaptați
`Problem.from_json`; restul codului lucrează doar cu atributele clasei.

Obiectivul e o sumă ponderată: w_benefit * beneficiu + w_equity * echitate.
Ponderile se pot schimba în timpul rulării (vedeți `apply_change`).

Extensie față de kit: interacțiuni pe perechi, opționale în JSON (`interactions`).
Două intervenții ale căror zone de influență se suprapun nu își adună integral beneficiile:
beneficiu(x) = Σ b_i x_i − Σ_{i<j} r_ij x_i x_j (la fel pentru echitate). Fără `interactions`,
problema e exact cea din kit (liniară).
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Problem:
    name: str
    kind: str                      # "binary" sau "integer"
    budget: float
    ids: list[str]
    cost: np.ndarray               # binary: costul fiecărei intervenții
    benefit: np.ndarray            # binary: beneficiul; integer: beneficiul maxim a_i
    equity: np.ndarray             # scor de echitate pe element
    w_benefit: float = 1.0
    w_equity: float = 0.0
    available: np.ndarray | None = None      # False = intervenție devenită imposibilă
    requires: dict = field(default_factory=dict)   # binary: id -> id-ul de care depinde
    lower: np.ndarray | None = None          # integer
    upper: np.ndarray | None = None          # integer
    saturation: np.ndarray | None = None     # integer: b_i din a_i * (1 - exp(-x/b_i))
    meta: dict = field(default_factory=dict)
    red_b: np.ndarray | None = None          # redundanța pe perechi (beneficiu), simetrică, diagonală 0
    red_e: np.ndarray | None = None          # redundanța pe perechi (echitate)

    # ------------------------------------------------------------ citire
    @classmethod
    def from_json(cls, path: str | Path) -> "Problem":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        items = d["items"]
        kind = d.get("kind", "binary")
        p = cls(
            name=d.get("name", Path(path).stem), kind=kind, budget=float(d["budget"]),
            ids=[it["id"] for it in items],
            cost=np.array([float(it.get("cost", 1.0)) for it in items]),
            benefit=np.array([float(it["benefit"]) for it in items]),
            equity=np.array([float(it.get("equity", 0.0)) for it in items]),
            requires={it["id"]: it["requires"] for it in items if it.get("requires")},
            meta={k: v for k, v in d.items() if k not in ("items",)},
        )
        if kind == "integer":
            p.lower = np.array([int(it["lower"]) for it in items])
            p.upper = np.array([int(it["upper"]) for it in items])
            p.saturation = np.array([float(it["saturation"]) for it in items])
        p.available = np.ones(len(items), dtype=bool)
        if d.get("interactions"):
            idx = {k: i for i, k in enumerate(p.ids)}
            n = len(items)
            p.red_b, p.red_e = np.zeros((n, n)), np.zeros((n, n))
            for it in d["interactions"]:
                if it["i"] in idx and it["j"] in idx:
                    a, b = idx[it["i"]], idx[it["j"]]
                    p.red_b[a, b] = p.red_b[b, a] = float(it.get("benefit", 0.0))
                    p.red_e[a, b] = p.red_e[b, a] = float(it.get("equity", 0.0))
        return p

    @property
    def has_interactions(self) -> bool:
        return self.red_b is not None

    @property
    def n(self) -> int:
        return len(self.ids)

    def copy(self) -> "Problem":
        return copy.deepcopy(self)

    # ------------------------------------------------------------ evaluare
    def _values(self, x):
        x = np.asarray(x)
        if self.kind == "binary":
            if self.red_b is not None:
                xf = x.astype(float)
                return (self.benefit @ xf - 0.5 * xf @ self.red_b @ xf,
                        self.equity @ xf - 0.5 * xf @ self.red_e @ xf)
            return self.benefit @ x, self.equity @ x
        gain = self.benefit * (1.0 - np.exp(-x / self.saturation))
        return gain.sum(), (self.equity * gain).sum()

    def objective(self, x) -> float:
        """Valoarea ponderată, FĂRĂ verificarea fezabilității."""
        b, e = self._values(x)
        return float(self.w_benefit * b + self.w_equity * e)

    def objectives(self, x) -> tuple[float, float]:
        """(beneficiu, echitate) separat, pentru varianta cu două obiective."""
        b, e = self._values(x)
        return float(b), float(e)

    def total_cost(self, x) -> float:
        x = np.asarray(x)
        return float(self.cost @ x) if self.kind == "binary" else float(x.sum())

    def violations(self, x) -> dict:
        """Cât de mult încalcă x constrângerile (0 peste tot = fezabil)."""
        x = np.asarray(x)
        v = {"budget": max(0.0, self.total_cost(x) - self.budget)}
        if self.kind == "binary":
            v["unavailable"] = int((x.astype(bool) & ~self.available).sum())
            idx = {k: i for i, k in enumerate(self.ids)}
            v["requires"] = int(sum(1 for a, b in self.requires.items() if x[idx[a]] and not x[idx[b]]))
        else:
            hi = np.where(self.available, self.upper, 0)
            lo = np.where(self.available, self.lower, 0)
            v["bounds"] = float(np.clip(lo - x, 0, None).sum() + np.clip(x - hi, 0, None).sum())
        return v

    def is_feasible(self, x) -> bool:
        return all(val == 0 for val in self.violations(x).values())

    # ------------------------------------------------------------ schimbări
    def apply_change(self, change: dict) -> None:
        """Aplică o schimbare din fișierul de scenarii. Tipuri:
          {"type": "budget_scale", "factor": 0.7}
          {"type": "remove_item", "id": "S07"}
          {"type": "weights", "w_benefit": 0.5, "w_equity": 0.5}
        """
        t = change["type"]
        if t == "budget_scale":
            self.budget *= float(change["factor"])
        elif t == "remove_item":
            self.available[self.ids.index(change["id"])] = False
        elif t == "weights":
            self.w_benefit = float(change["w_benefit"])
            self.w_equity = float(change["w_equity"])
        else:
            raise ValueError(f"Tip de schimbare necunoscut: {t}")
