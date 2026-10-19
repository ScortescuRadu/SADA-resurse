"""Referința SUMO pe un coridor drept, cu aceeași geometrie ca automatul celular (GHID.md, pasul 7).

Construiește cu netconvert un coridor de model.length_m, cu model.lanes benzi, împărțit în muchii
de model.segment_m (o muchie = un tronson al automatului), cu un detector E1 pe fiecare bandă la
mijlocul fiecărui tronson. Rulează în SUMO scenariile din config (cererea constantă, incidentul ca
vehicul oprit, vârful de cerere dacă îl adăugați cu cheia `surge`) și o rampă de cerere pentru
diagrama fundamentală.

    python scripts/sumo_coridor_drept.py              # 5 seed-uri pe scenariu
    python scripts/sumo_coridor_drept.py --runs 10

Ieșiri:
  data/sumo/coridor_drept.net.xml       rețeaua
  results/sumo/sumo_results.csv         pe rulare: travel_time_mean, throughput, wait_mean
  results/sumo/sumo_speed.csv           viteza medie pe tronson la fiecare 10 s (pentru timpul de revenire)
  results/sumo/fd_sumo.csv              puncte (densitate, flux, viteză) din detectoare, la 60 s

De ce un coridor drept și nu rețeaua din OSM: ca diferențele dintre SUMO și automat să vină din
model (Krauss vs. NaSch), nu din intersecții și semafoare pe care automatul nu le are.
Vehiculul SUMO are lungime + minGap = 7,5 m, adică exact o celulă.

Timpul de revenire după incident nu e calculat aici: definiți-l voi, la fel ca pentru automat,
din sumo_speed.csv. Altfel comparația nu e corectă.
"""
from __future__ import annotations

import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from sada.config import load_config
from sada.p1.sumo_tools import find_binary, read_e1_output

OUT = Path("results/sumo")
NET = Path("data/sumo/coridor_drept.net.xml")
WORK = Path("data/sumo/ref")


def write(root, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def build_net(m) -> list[str]:
    n_seg = int(round(m["length_m"] / m["segment_m"]))
    seg_len = m["length_m"] / n_seg
    v = m["vmax"] * m["cell_m"] / m["dt_s"]
    nodes, edges = ET.Element("nodes"), ET.Element("edges")
    for i in range(n_seg + 1):
        ET.SubElement(nodes, "node", id=f"n{i}", x=f"{i * seg_len:.1f}", y="0", type="priority")
    ids = []
    for i in range(n_seg):
        ids.append(f"e{i}")
        ET.SubElement(edges, "edge", id=f"e{i}", **{"from": f"n{i}", "to": f"n{i + 1}"},
                      numLanes=str(m["lanes"]), speed=f"{v:.2f}")
    write(nodes, WORK / "c.nod.xml")
    write(edges, WORK / "c.edg.xml")
    subprocess.run([find_binary("netconvert"), "-n", str(WORK / "c.nod.xml"), "-e", str(WORK / "c.edg.xml"),
                    "-o", str(NET), "--no-turnarounds", "true"], check=True, capture_output=True)
    return ids


def vtype(root, m):
    # lungime + minGap = 7,5 m = o celulă; maxSpeed = vmax; sigma ≈ încetinirea aleatoare
    ET.SubElement(root, "vType", id="car", accel="2.6", decel="4.5", sigma="0.5", length="5",
                  minGap="2.5", maxSpeed=f"{m['vmax'] * m['cell_m'] / m['dt_s']:.2f}")


def flow(root, fid, edges, begin, end, veh_h):
    # probability = sosiri Bernoulli pe secundă, ca procesul Poisson din automat
    ET.SubElement(root, "flow", id=fid, type="car", begin=str(begin), end=str(end),
                  probability=f"{min(1.0, veh_h / 3600):.4f}", departLane="best", departSpeed="max",
                  route="r")


def write_routes(path, edges, scen, m):
    root = ET.Element("routes")
    vtype(root, m)
    ET.SubElement(root, "route", id="r", edges=" ".join(edges))
    T = m["duration_s"]
    surge = scen.get("surge")
    if surge:
        s0, s1 = surge["start_s"], surge["start_s"] + surge["duration_s"]
        flow(root, "f0", edges, 0, s0, scen["inflow_veh_h"])
        flow(root, "f1", edges, s0, s1, surge["inflow_veh_h"])
        flow(root, "f2", edges, s1, T, scen["inflow_veh_h"])
    elif "ramp" in scen:
        q0, q1, steps = scen["ramp"]
        for i, q in enumerate(np.linspace(q0, q1, steps)):
            b = i * T // steps
            flow(root, f"f{i}", edges, b, (i + 1) * T // steps, q)
    else:
        flow(root, "f0", edges, 0, T, scen["inflow_veh_h"])
    inc = scen.get("incident")
    if inc:
        seg_len = m["length_m"] / len(edges)
        e = min(int(inc["position_m"] // seg_len), len(edges) - 1)
        if inc["position_m"] % seg_len == 0 and e > 0:   # la granița dintre muchii: capătul muchiei din amonte
            e -= 1
        pos = inc["position_m"] - e * seg_len
        pos = min(max(pos, 6.0), seg_len - 1.0)
        veh = ET.SubElement(root, "vehicle", id="incident", type="car", depart=str(inc["start_s"]),
                            departLane=str(inc["lane"]), departPos=f"{pos - 1:.1f}", departSpeed="0",
                            insertionChecks="none")
        ET.SubElement(veh, "route", edges=" ".join(edges[e:]))
        ET.SubElement(veh, "stop", lane=f"{edges[e]}_{inc['lane']}", endPos=f"{pos:.1f}",
                      duration=str(inc["duration_s"]))
    # SUMO cere vehiculele sortate după momentul plecării
    items = sorted(list(root), key=lambda el: (el.tag not in ("vType", "route"), float(el.get("begin", el.get("depart", 0)))))
    for el in list(root):
        root.remove(el)
    root.extend(items)
    write(root, path)


def write_detectors(path, edges, m, period, out_file):
    root = ET.Element("additional")
    seg_len = m["length_m"] / len(edges)
    for i, e in enumerate(edges):
        for ln in range(m["lanes"]):
            ET.SubElement(root, "inductionLoop", id=f"d{i}_{ln}", lane=f"{e}_{ln}", pos=f"{seg_len / 2:.1f}",
                          period=str(period), file=out_file)
    write(root, path)


def run(name, scen, seed, edges, m, period=10):
    d = WORK / f"{name}_{seed}"
    d.mkdir(parents=True, exist_ok=True)
    write_routes(d / "routes.rou.xml", edges, scen, m)
    write_detectors(d / "det.add.xml", edges, m, period, "e1.xml")
    cmd = [find_binary("sumo"), "-n", str(NET.resolve()), "-r", "routes.rou.xml", "-a", "det.add.xml",
           "--seed", str(seed), "--step-length", str(m["dt_s"]), "--end", str(m["duration_s"]),
           "--tripinfo-output", "trips.xml", "--no-step-log", "true", "--duration-log.disable", "true",
           "--no-warnings", "true", "--lanechange.duration", "0", "--collision.action", "none"]
    subprocess.run(cmd, cwd=d, check=True, capture_output=True)
    trips = pd.DataFrame([t.attrib for t in ET.parse(d / "trips.xml").getroot().iter("tripinfo")])
    e1 = read_e1_output(d / "e1.xml")
    return trips, e1


def fd_points(e1, m):
    """Densitate = flux / viteză, pe bandă, intervale agregate la 60 s."""
    e = e1.copy()
    e["bin"] = (e["begin"] // 60).astype(int)
    g = e.groupby(["id", "bin"]).agg(n=("n_veh", "sum"), v=("speed_m_s", lambda s: s[s >= 0].mean()))
    g = g[g["n"] > 0].dropna()
    g["flow_veh_h"] = g["n"] * 60.0
    g["speed_km_h"] = g["v"] * 3.6
    g["density_veh_km"] = g["flow_veh_h"] / g["speed_km_h"].clip(lower=1.0)
    return g.reset_index()[["id", "bin", "density_veh_km", "flow_veh_h", "speed_km_h"]]



def metrics(trips, m):
    warm, T = m["warmup_s"], m["duration_s"]
    trips = trips[trips["id"] != "incident"].copy()
    for c in ("arrival", "duration", "departDelay"):
        trips[c] = trips[c].astype(float)
    sel = trips["arrival"] > warm
    return {"travel_time_mean": trips.loc[sel, "duration"].mean(),
            "throughput": sel.sum() / ((T - warm) / 3600),
            "wait_mean": trips.loc[trips["arrival"] - trips["duration"] > warm, "departDelay"].mean()}


def speed_series(e1, edges, m):
    """Viteza medie [km/h] pe tronson și interval, ponderată cu vehiculele numărate."""
    e = e1[e1["speed_m_s"] >= 0].copy()
    e["segment"] = e["id"].str.extract(r"d(\d+)_")[0].astype(int)
    g = e.groupby(["end", "segment"]).apply(
        lambda x: np.average(x["speed_m_s"], weights=x["n_veh"].clip(lower=1)) * 3.6, include_groups=False)
    return g.rename("speed_km_h").reset_index().rename(columns={"end": "t_s"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--runs", type=int, default=5)
    a = ap.parse_args()
    cfg = load_config(a.config)
    m = cfg["model"]
    OUT.mkdir(parents=True, exist_ok=True)
    edges = build_net(m)
    print(f"Rețea: {NET} ({len(edges)} muchii de {m['segment_m']} m, {m['lanes']} benzi)")
    seeds = [cfg["experiment"]["base_seed"] + i for i in range(a.runs)]
    rows, speeds = [], []
    for sname, scen in cfg["scenarios"].items():
        for seed in seeds:
            trips, e1 = run(sname, scen, seed, edges, m)
            rows.append({"scenario": sname, "variant": "sumo", "seed": seed, **metrics(trips, m)})
            speeds.append(speed_series(e1, edges, m).assign(scenario=sname, seed=seed))
        r = pd.DataFrame([x for x in rows if x["scenario"] == sname])
        print(f"  {sname:16s} timp de parcurs {r.travel_time_mean.mean():6.1f} s, debit {r.throughput.mean():6.0f} veh/h")
    pd.DataFrame(rows).to_csv(OUT / "sumo_results.csv", index=False)
    pd.concat(speeds).to_csv(OUT / "sumo_speed.csv", index=False)

    # diagrama fundamentală: rampă de cerere până peste capacitate, plus un incident
    # ca să apară și ramura congestionată
    T = m["duration_s"]
    fd_scen = {"ramp": (300, 3600, 12), "incident": {"lane": 0, "position_m": m["length_m"] * 0.75,
                                                     "start_s": int(T * 0.6), "duration_s": int(T * 0.3)}}
    pts = []
    for seed in seeds[:3]:
        _, e1 = run("fd", fd_scen, seed, edges, m, period=60)
        pts.append(fd_points(e1, m).assign(seed=seed))
    pd.concat(pts).to_csv(OUT / "fd_sumo.csv", index=False)
    print(f"Salvat în {OUT}/")


if __name__ == "__main__":
    main()
