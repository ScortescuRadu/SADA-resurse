"""Unelte pentru bucla Langton / Byl (GHID.md, pasul 7). Nu e analiza; e doar ce trebuie ca
analiza să se poată face corect.

    from sada.p3.verificare_golly import verify_against_tree, find_copies, CopyTracker

1. verify_against_tree(rule) compară tabelul pe care îl construiește ca.TableCA din @TABLE cu
   arborele @TREE din același fișier. Golly simulează cu arborele, așa că dacă cele două
   coincid pe toate vecinătățile, fiecare pas al vostru e identic cu pasul din Golly. Asta
   înlocuiește comparația „cu ochiul” cu Golly, pe care o cere GHID-ul.
2. find_copies(grid, pattern) găsește aparițiile exacte ale configurației inițiale (în toate
   cele 4 rotații) pe grilă.
3. CopyTracker numără buclele DISTINCTE văzute de la început. De ce e nevoie de el: buclele
   unei colonii trec prin configurația inițială la momente diferite, iar mama trece prin ea
   rotită, pe loc. Dacă numărați copiile exacte la un singur pas, veți vedea 0 sau 1 aproape
   mereu. Trebuie să le apelați la FIECARE pas, pentru că o buclă e în forma exactă un singur pas.

Ce rămâne de făcut: rularea coloniei, perioada de replicare, perturbările și clasificarea
lor, comparația cu refacerea rutelor.
"""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np

from .ca import RuleTable, TableCA


# ---- @TREE --------------------------------------------------------------------
def read_tree(path: str | Path) -> tuple[int, int, list]:
    """(n_states, n_neighbors, nodes) din secțiunea @TREE. Fiecare nod e (nivel, copii)."""
    sec, n_states, n_nb, nodes = None, None, None, []
    for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("@"):
            sec = line.split()[0]
            continue
        if sec != "@TREE":
            continue
        if line.startswith("num_states"):
            n_states = int(line.split("=")[1])
        elif line.startswith("num_neighbors"):
            n_nb = int(line.split("=")[1])
        elif line.startswith("num_nodes"):
            pass
        else:
            vals = list(map(int, line.split()))
            nodes.append((vals[0], vals[1:]))
    if not nodes:
        raise ValueError(f"{path} nu are secțiune @TREE")
    return n_states, n_nb, nodes


def tree_lookup(path: str | Path, order: str = "NWESC") -> np.ndarray:
    """Tabelul de tranziții dat de arborele Golly, indexat ca în TableCA:
    cod = (((C·k + N)·k + E)·k + S)·k + W. `order` e ordinea în care arborele consumă
    variabilele, de la rădăcină la frunze (Golly, vecinătate von Neumann: N, W, E, S, C)."""
    k, n_nb, nodes = read_tree(path)
    if n_nb != 4:
        raise ValueError("doar vecinătatea von Neumann (4 vecini)")
    root = len(nodes) - 1
    table = np.zeros(k ** 5, dtype=np.int16)
    for C, N, E, S, W in itertools.product(range(k), repeat=5):
        val = dict(C=C, N=N, E=E, S=S, W=W)
        node = root
        for var in order:
            lvl, kids = nodes[node]
            node = kids[val[var]]
        table[(((C * k + N) * k + E) * k + S) * k + W] = node
    return table


def verify_against_tree(rule_path: str | Path) -> dict:
    """Compară tabelul din @TABLE (cititorul kitului) cu arborele Golly, pe toate vecinătățile."""
    ca = TableCA(RuleTable.from_file(rule_path))
    tree = tree_lookup(rule_path)
    diff = int((ca.table != tree).sum())
    return {"neighbourhoods": int(len(tree)), "differences": diff, "identical": diff == 0}


# ---- replicarea ---------------------------------------------------------------
def rotations(pattern: np.ndarray) -> list[np.ndarray]:
    return [np.rot90(pattern, r) for r in range(4)]


def find_copies(grid: np.ndarray, pattern: np.ndarray) -> list[tuple[int, int, int]]:
    """Pozițiile (rând, coloană, rotație) unde apare exact configurația `pattern`
    (inclusiv celulele goale din interiorul dreptunghiului). Candidații se filtrează celulă
    cu celulă, începând cu celulele nenule ale modelului, deci costul scade repede."""
    out = []
    H, W = grid.shape
    for r, p in enumerate(rotations(pattern)):
        h, w = p.shape
        if H < h or W < w:
            continue
        cells = sorted(np.ndindex(h, w), key=lambda ij: p[ij] == 0)
        i0, j0 = cells[0]
        ci, cj = np.nonzero(grid[i0:H - h + 1 + i0, j0:W - w + 1 + j0] == p[i0, j0])
        for i, j in cells[1:]:
            if not len(ci):
                break
            keep = grid[ci + i, cj + j] == p[i, j]
            ci, cj = ci[keep], cj[keep]
        out += [(int(i), int(j), r) for i, j in zip(ci, cj)]
    return out


class CopyTracker:
    """Buclele distincte văzute până acum (după centrul copiei exacte)."""

    def __init__(self, pattern: np.ndarray, min_dist: float | None = None):
        # implicit: jumătate din latura mare a modelului (7,5 celule la Langton, 2 la Byl)
        self.pattern, self.centers = pattern, []
        self.min_dist = min_dist if min_dist is not None else 0.5 * max(pattern.shape)

    def update(self, grid) -> int:
        new = 0
        for i, j, r in find_copies(grid, self.pattern):
            h, w = rotations(self.pattern)[r].shape
            c = (i + h / 2, j + w / 2)
            if all((c[0] - a) ** 2 + (c[1] - b) ** 2 > self.min_dist ** 2 for a, b in self.centers):
                self.centers.append(c)
                new += 1
        return new

    @property
    def count(self) -> int:
        return len(self.centers)
