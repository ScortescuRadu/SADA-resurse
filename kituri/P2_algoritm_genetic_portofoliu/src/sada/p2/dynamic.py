"""Programul de schimbări: aplică modificările problemei la generațiile stabilite.

Schimbarea se aplică din afara algoritmului genetic, asupra problemei. Algoritmul
nu primește niciun semnal; trebuie să o detecteze singur (bucla MAPE-K).

Formatul fișierului (vedeți data/dev/changes_*.json):
    {"changes": [
        {"generation": 100, "type": "budget_scale", "factor": 0.7},
        {"generation": 200, "type": "remove_item", "id": "S07"},
        {"generation": 300, "type": "weights", "w_benefit": 0.5, "w_equity": 0.5}
    ]}
"""
from __future__ import annotations

import json
from pathlib import Path

from .problem import Problem


class ChangeSchedule:
    def __init__(self, changes: list[dict]):
        self.changes = sorted(changes, key=lambda c: c["generation"])

    @classmethod
    def from_json(cls, path: str | Path) -> "ChangeSchedule":
        return cls(json.loads(Path(path).read_text(encoding="utf-8"))["changes"])

    @property
    def generations(self) -> list[int]:
        return [c["generation"] for c in self.changes]

    def apply(self, problem: Problem, generation: int) -> list[dict]:
        """Aplică schimbările programate exact la această generație. Întoarce lista lor."""
        due = [c for c in self.changes if c["generation"] == generation]
        for c in due:
            problem.apply_change(c)
        return due
