"""Stil comun pentru figuri și salvare în PDF + PNG."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # funcționează și fără ecran (servere, WSL)
import matplotlib.pyplot as plt  # noqa: E402


def setup_style() -> None:
    plt.rcParams.update({
        "figure.figsize": (6.0, 3.6), "figure.dpi": 120, "savefig.bbox": "tight",
        "font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    })


def savefig(fig, path: str | Path) -> None:
    """Salvează figura ca PDF (pentru raport) și PNG (pentru prezentare)."""
    path = Path(path)
    if path.suffix in (".pdf", ".png", ".svg"):
        path = path.with_suffix("")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.parent / f"{path.name}.pdf")
    fig.savefig(path.parent / f"{path.name}.png", dpi=200)
    plt.close(fig)
