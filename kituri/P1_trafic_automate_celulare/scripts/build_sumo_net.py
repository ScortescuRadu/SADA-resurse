"""Construiește rețeaua SUMO din extrasul OSM, cu netconvert.

    python scripts/build_sumo_net.py                       # citește osm.out din config
    python scripts/build_sumo_net.py --osm data/p1_coridor/coridor.osm

Opțiunile sunt cele recomandate în documentația SUMO pentru importul OSM.
Deschideți rezultatul în netedit (vine cu eclipse-sumo) ca să verificați
coridorul și să aflați ID-urile muchiilor de început și sfârșit (pentru config).
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from sada.config import load_config
from sada.p1.sumo_tools import find_binary

OPTIONS = [
    "--geometry.remove", "--ramps.guess", "--junctions.join",
    "--tls.guess-signals", "--tls.discard-simple", "--tls.join",
    "--remove-edges.isolated", "--keep-edges.components", "1",
    "--output.street-names", "--output.original-names",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--osm")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = load_config(a.config)
    osm = Path(a.osm or cfg["osm"]["out"])
    out = Path(a.out or cfg["sumo"]["net"])
    if not osm.exists():
        raise SystemExit(f"Nu există {osm}. Rulați întâi scripts/download_osm.py sau copiați extrasul din pachet.")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [find_binary("netconvert"), "--osm-files", str(osm), "-o", str(out), *OPTIONS]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"\nRețea scrisă în {out}. Verificați-o cu:  netedit {out}")


if __name__ == "__main__":
    main()
