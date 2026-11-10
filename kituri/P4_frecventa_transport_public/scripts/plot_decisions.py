"""Desenează o măsurătoare din jurnalul controllerului, cu deciziile marcate.

    python scripts/plot_decisions.py results/logs/demo.jsonl --key <cheie>

Cheia este numele unei măsurători din câmpul `measurements` al jurnalului (de
exemplu `mean_speed`). Dacă măsurătoarea e un vector (una pe tronson, pe
linie etc.), alegeți elementul cu --index. Fără --key, scriptul afișează
cheile disponibile.
"""
from __future__ import annotations

import argparse

from sada.timeline import plot_timeline, read_log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--key")
    ap.add_argument("--index", type=int)
    ap.add_argument("--ylabel")
    ap.add_argument("--out", default="results/figures/decisions")
    a = ap.parse_args()
    log = read_log(a.log)
    if log.empty:
        raise SystemExit("Jurnalul e gol. Controllerul a luat vreo decizie? (log_every_step=True scrie toți pașii)")
    meas = log["measurements"].dropna()
    keys = sorted({k for m in meas if isinstance(m, dict) for k in m})
    if not a.key:
        print(f"{len(log)} intrări. Chei disponibile în measurements: {keys}")
        return
    def val(m):
        v = m.get(a.key) if isinstance(m, dict) else None
        if isinstance(v, (list, tuple)) and a.index is not None:
            return v[a.index]
        return v
    y = log["measurements"].map(val)
    plot_timeline(log["t"], y, log, a.out, ylabel=a.ylabel or a.key, title=f"{a.key} și deciziile controllerului")
    print(f"Salvat {a.out}.pdf. Pentru o curbă continuă, porniți controllerul cu log_every_step=True.")


if __name__ == "__main__":
    main()
