"""Descarcă din OpenStreetMap (prin Overpass API) străzile din dreptunghiul
osm.bbox din config. Folosiți-l dacă vreți să refaceți rețeaua SUMO sau să
lucrați pe alt coridor; pachetul disciplinei conține deja extrasul.

    python scripts/download_osm.py
    python scripts/download_osm.py --bbox 21.20 45.74 21.26 45.77

Datele OSM: © OpenStreetMap contributors, licența ODbL. Notați în data/DATA.md
data descărcării și dreptunghiul folosit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from sada.config import load_config

ENDPOINTS = ["https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter"]
# doar drumurile pe care circulă mașini
HIGHWAYS = ("motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|"
            "motorway_link|trunk_link|primary_link|secondary_link|tertiary_link")


def build_query(lon_min, lat_min, lon_max, lat_max) -> str:
    bb = f"{lat_min},{lon_min},{lat_max},{lon_max}"   # Overpass: sud, vest, nord, est
    return f'[out:xml][timeout:180];(way["highway"~"^({HIGHWAYS})$"]({bb});>;);out body;'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"))
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = load_config(a.config)
    bbox = a.bbox or cfg["osm"]["bbox"]
    out = Path(a.out or cfg["osm"]["out"])
    out.parent.mkdir(parents=True, exist_ok=True)

    data = urllib.parse.urlencode({"data": build_query(*bbox)}).encode()
    for url in ENDPOINTS:
        try:
            print(f"Descarc de la {url} ...")
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "SADA-student-project"})
            with urllib.request.urlopen(req, timeout=240) as r:
                content = r.read()
            if b"<osm" not in content[:500]:
                raise RuntimeError(content[:300].decode(errors="replace"))
            out.write_bytes(content)
            print(f"Salvat {out} ({len(content) / 1e6:.1f} MB)")
            print(f"Pentru data/DATA.md: OpenStreetMap via Overpass, bbox={bbox}, "
                  f"{dt.date.today().isoformat()}, ODbL")
            return
        except Exception as e:
            print(f"  eșec: {e}")
            time.sleep(2)
    sys.exit("Nu am putut descărca. Încercați mai târziu sau micșorați dreptunghiul "
             "(Overpass refuză zone prea mari). Alternativă: exportul manual de pe openstreetmap.org.")


if __name__ == "__main__":
    main()
