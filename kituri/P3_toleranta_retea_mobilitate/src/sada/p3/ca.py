"""Automat celular cu vecinătate von Neumann, cu reguli în formatul Golly (@TABLE)
și modele inițiale în format RLE. Se folosește pentru bucla Langton sau Byl
(GHID.md, pasul 7).

    from sada.p3.ca import RuleTable, read_rle, TableCA
    rule = RuleTable.from_file("data/ca/Langtons-Loops.rule")
    pattern = read_rle("data/ca/Langtons-Loops.rle")
    ca = TableCA(rule)
    grid = ca.place(pattern, shape=(128, 128))
    for _ in range(1000): grid = ca.step(grid)

Formatul @TABLE (pe scurt): după n_states, neighborhood și symmetries vin
tranzițiile, câte una pe linie, în ordinea C,N,E,S,W,C' (celula, vecinii nord,
est, sud, vest, starea nouă). Pentru n_states ≤ 10 virgulele pot lipsi
("000012"). Variabilele (var a={0,1,2}) acoperă mai multe valori; aceeași
variabilă de două ori pe o linie înseamnă aceeași valoare. Prima tranziție care
se potrivește câștigă; dacă nu se potrivește niciuna, celula își păstrează starea.
"""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class RuleTable:
    name: str
    n_states: int
    transitions: dict = field(default_factory=dict)   # (C,N,E,S,W) -> C'

    @classmethod
    def from_file(cls, path: str | Path) -> "RuleTable":
        return cls.from_text(Path(path).read_text(encoding="utf-8", errors="replace"))

    @classmethod
    def from_text(cls, text: str) -> "RuleTable":
        name, section = "rule", None
        n_states, neigh, sym = None, None, "none"
        variables: dict[str, list[int]] = {}
        lines = []
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if line.startswith("@"):
                parts = line.split()
                section = parts[0]
                if section == "@RULE" and len(parts) > 1:
                    name = parts[1]
                continue
            if section not in (None, "@TABLE"):
                continue
            if line.startswith("n_states:"):
                n_states = int(line.split(":")[1])
            elif line.startswith("neighborhood:"):
                neigh = line.split(":")[1].strip()
            elif line.startswith("symmetries:"):
                sym = line.split(":")[1].strip()
            elif line.startswith("var "):
                m = re.match(r"var\s+(\w+)\s*=\s*\{(.*)\}", line)
                vals = []
                for tok in m.group(2).split(","):
                    tok = tok.strip()
                    vals += variables[tok] if tok in variables else [int(tok)]
                variables[m.group(1)] = vals
            else:
                lines.append(line)
        if neigh != "vonNeumann":
            raise ValueError(f"Doar vecinătatea von Neumann e suportată (fișierul are: {neigh})")
        rule = cls(name=name, n_states=n_states)
        for line in lines:
            toks = [t.strip() for t in line.split(",")] if "," in line else list(line.replace(" ", ""))
            if len(toks) != 6:
                raise ValueError(f"Tranziție cu {len(toks)} elemente în loc de 6: {line}")
            names = sorted({t for t in toks if t in variables})
            for combo in itertools.product(*(variables[v] for v in names)):
                bind = dict(zip(names, combo))
                vals = [bind[t] if t in bind else int(t) for t in toks]
                c, nbrs, new = vals[0], vals[1:5], vals[5]
                for key in _symmetric(nbrs, sym):
                    rule.transitions.setdefault((c, *key), new)
        return rule


def _symmetric(nbrs, sym):
    n, e, s, w = nbrs
    rots = [(n, e, s, w), (w, n, e, s), (s, w, n, e), (e, s, w, n)]
    refl = [(a, d, c, b) for a, b, c, d in rots]          # oglindire stânga-dreapta
    if sym == "none":
        return [(n, e, s, w)]
    if sym == "rotate4":
        return rots
    if sym == "rotate4reflect":
        return rots + refl
    if sym == "reflect_horizontal":
        return [(n, e, s, w), (n, w, s, e)]
    if sym == "permute":
        return list(itertools.permutations((n, e, s, w)))
    raise ValueError(f"Simetrie nesuportată: {sym}")


class TableCA:
    """Aplică un RuleTable pe o grilă NumPy, vectorizat (un tabel de căutare)."""

    def __init__(self, rule: RuleTable):
        self.rule = rule
        k = rule.n_states
        codes = np.arange(k ** 5)
        self.table = (codes // k ** 4).astype(np.int16)          # implicit: starea rămâne
        for (c, n, e, s, w), new in rule.transitions.items():
            self.table[(((c * k + n) * k + e) * k + s) * k + w] = new

    def step(self, grid: np.ndarray, wrap: bool = False) -> np.ndarray:
        k = self.rule.n_states
        if wrap:
            N, S = np.roll(grid, 1, 0), np.roll(grid, -1, 0)
            W, E = np.roll(grid, 1, 1), np.roll(grid, -1, 1)
            C = grid
        else:
            P = np.pad(grid, 1)
            C, N, S, W, E = P[1:-1, 1:-1], P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]
        code = (((C.astype(np.int64) * k + N) * k + E) * k + S) * k + W
        return self.table[code]

    @staticmethod
    def place(pattern: np.ndarray, shape=(128, 128), offset=None) -> np.ndarray:
        grid = np.zeros(shape, dtype=np.int16)
        r0, c0 = offset if offset else ((shape[0] - pattern.shape[0]) // 2, (shape[1] - pattern.shape[1]) // 2)
        grid[r0:r0 + pattern.shape[0], c0:c0 + pattern.shape[1]] = pattern
        return grid


def read_rle(path: str | Path) -> np.ndarray:
    """Citește un model RLE (formatul Golly) cu până la 24 de stări."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    body, width, height = [], None, None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("x"):
            m = re.search(r"x\s*=\s*(\d+).*?y\s*=\s*(\d+)", line)
            width, height = int(m.group(1)), int(m.group(2))
            continue
        body.append(line)
    rows, row, count = [], [], ""
    for ch in "".join(body):
        if ch.isdigit():
            count += ch
            continue
        n = int(count) if count else 1
        count = ""
        if ch in "b.":
            row += [0] * n
        elif ch == "o":
            row += [1] * n
        elif "A" <= ch <= "X":
            row += [ord(ch) - ord("A") + 1] * n
        elif ch == "$":
            rows.append(row)
            rows += [[] for _ in range(n - 1)]
            row = []
        elif ch == "!":
            break
        else:
            raise ValueError(f"Simbol RLE nesuportat: {ch!r} (doar până la 24 de stări)")
    rows.append(row)
    width = width or max(len(r) for r in rows)
    height = height or len(rows)
    grid = np.zeros((height, width), dtype=np.int16)
    for i, r in enumerate(rows[:height]):
        grid[i, :len(r)] = r[:width]
    return grid


def count_structures(grid: np.ndarray, min_cells: int = 20) -> int:
    """Numărul de structuri separate (componente de celule nenule, conexitate 8)
    cu cel puțin min_cells celule. Util pentru numărarea buclelor replicate."""
    from scipy import ndimage
    lab, n = ndimage.label(grid > 0, structure=np.ones((3, 3)))
    if n == 0:
        return 0
    sizes = np.bincount(lab.ravel())[1:]
    return int((sizes >= min_cells).sum())
