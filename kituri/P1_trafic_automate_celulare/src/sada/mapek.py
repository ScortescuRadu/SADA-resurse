"""Bucla MAPE-K (Monitor, Analyze, Plan, Execute + Knowledge).

Fiecare proiect își definește propriul controller moștenind clasa `Controller`
și completând cele patru metode. Metoda `step` le apelează în ordine și scrie
fiecare decizie în jurnal (baza de cunoștințe K).

Exemplu complet, care rulează: examples/toy_mapek.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Knowledge:
    """Baza de cunoștințe K: configurația, istoricul deciziilor și orice stare internă."""
    config: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    state: dict = field(default_factory=dict)


def _to_jsonable(obj: Any):
    if hasattr(obj, "tolist"):          # vectori și scalari NumPy
        return obj.tolist()
    if isinstance(obj, (set, tuple)):
        return list(obj)
    return repr(obj)


class Controller:
    """Clasa de bază. Suprascrieți monitor, analyze, plan și execute."""

    def __init__(self, config: dict | None = None, log_path: str | Path | None = None,
                 log_every_step: bool = False):
        self.k = Knowledge(config=dict(config or {}))
        self.log_every_step = log_every_step
        self.log_path = Path(log_path) if log_path else None
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.write_text("", encoding="utf-8")

    # ---- cele patru etape -------------------------------------------------
    def monitor(self, system, t):
        """Citește măsurătorile din sistem. Întoarce un dicționar."""
        raise NotImplementedError

    def analyze(self, measurements, t):
        """Interpretează măsurătorile (ex. 'liber' / 'aglomerat'). Întoarce o evaluare."""
        raise NotImplementedError

    def plan(self, assessment, t):
        """Alege o acțiune sau întoarce None dacă nu trebuie schimbat nimic."""
        raise NotImplementedError

    def execute(self, system, action, t):
        """Aplică acțiunea asupra sistemului, fără să-l oprească."""
        raise NotImplementedError

    # ---- ciclul complet ---------------------------------------------------
    def step(self, system, t):
        measurements = self.monitor(system, t)
        assessment = self.analyze(measurements, t)
        action = self.plan(assessment, t)
        if action is not None:
            self.execute(system, action, t)
        if action is not None or self.log_every_step:
            self.log(t=t, measurements=measurements, assessment=assessment, action=action)
        return action

    def log(self, **entry) -> None:
        self.k.history.append(entry)
        if self.log_path:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=_to_jsonable) + "\n")


class FixedController(Controller):
    """Varianta de referință: nu schimbă nimic. Folosiți-o ca „fără adaptare”."""

    def monitor(self, system, t):
        return None

    def analyze(self, measurements, t):
        return None

    def plan(self, assessment, t):
        return None

    def execute(self, system, action, t):
        pass
