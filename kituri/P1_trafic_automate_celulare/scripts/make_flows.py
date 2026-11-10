"""Generează fișierul de cerere pentru SUMO (elemente <flow>) din profilul orar.

Profilul e un CSV cu coloanele `hour,veh_per_hour` (cel din pachet sau unul propriu).
Fără CSV, --synthetic creează o cerere cu vârf de dimineață, utilă pentru teste.

    python scripts/make_flows.py --profile data/p1_coridor/profil_flux.csv
    python scripts/make_flows.py --synthetic --peak 1800 --base 400

Muchiile de intrare și ieșire (sumo.from_edge, sumo.to_edge) se completează în config.
Dacă numele coloanelor din pachet diferă, folosiți --hour-col și --flow-col.
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from sada.config import load_config


def synthetic_profile(base: float, peak: float, peak_hour: float = 8.0, width_h: float = 1.0) -> pd.DataFrame:
    hours = np.arange(5, 12)
    flow = base + (peak - base) * np.exp(-0.5 * ((hours + 0.5 - peak_hour) / width_h) ** 2)
    return pd.DataFrame({"hour": hours, "veh_per_hour": flow.round()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--profile")
    ap.add_argument("--hour-col", default="hour")
    ap.add_argument("--flow-col", default="veh_per_hour")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--base", type=float, default=400)
    ap.add_argument("--peak", type=float, default=1800)
    ap.add_argument("--start-hour", type=int, default=None,
                    help="ora care devine t=0 în simulare (implicit: prima oră din profil)")
    a = ap.parse_args()
    cfg = load_config(a.config)
    src, dst = cfg["sumo"]["from_edge"], cfg["sumo"]["to_edge"]
    if "TODO" in (src, dst):
        raise SystemExit("Completați sumo.from_edge și sumo.to_edge în config (ID-uri din netedit).")

    if a.synthetic:
        prof = synthetic_profile(a.base, a.peak)
    elif a.profile:
        prof = pd.read_csv(a.profile).rename(columns={a.hour_col: "hour", a.flow_col: "veh_per_hour"})
    else:
        raise SystemExit("Dați --profile <fișier.csv> sau --synthetic.")
    h0 = a.start_hour if a.start_hour is not None else int(prof["hour"].min())

    root = ET.Element("routes")
    ET.SubElement(root, "vType", id="car", accel="2.6", decel="4.5", sigma="0.5",
                  length="5", minGap="2.5", maxSpeed="13.89")
    for _, r in prof.iterrows():
        b = (int(r["hour"]) - h0) * 3600
        ET.SubElement(root, "flow", id=f"f{int(r['hour']):02d}", type="car", begin=str(b), end=str(b + 3600),
                      vehsPerHour=f"{float(r['veh_per_hour']):.0f}", departLane="best", departSpeed="max",
                      **{"from": src, "to": dst})
    out = Path(cfg["sumo"]["flows"])
    out.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    print(prof.to_string(index=False))
    print(f"\nScris {out}  (t=0 corespunde orei {h0}:00)")


if __name__ == "__main__":
    main()
