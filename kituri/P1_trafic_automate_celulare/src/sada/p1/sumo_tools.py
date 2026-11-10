"""Unelte pentru referința SUMO: găsirea programelor, detectoare E1, rulare prin TraCI.

Exemplu:
    from sada.p1.sumo_tools import write_e1_detectors, run_sumo, read_e1_output
    write_e1_detectors([("d0", "123456#0_0", 50.0)], "data/sumo/det.add.xml")
    run_sumo("data/sumo/coridor.net.xml", "data/sumo/flows.rou.xml",
             "data/sumo/det.add.xml", end_s=3600, seed=1)
    df = read_e1_output("data/sumo/e1.xml")
"""
from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


def sumo_home() -> Path | None:
    if os.environ.get("SUMO_HOME"):
        return Path(os.environ["SUMO_HOME"])
    try:
        import sumo  # pachetul pip eclipse-sumo
        return Path(sumo.SUMO_HOME)
    except ImportError:
        return None


def find_binary(name: str) -> str:
    """Calea către sumo, sumo-gui, netconvert etc."""
    p = shutil.which(name)
    if p:
        return p
    home = sumo_home()
    if home:
        for cand in (home / "bin" / name, home / "bin" / f"{name}.exe"):
            if cand.exists():
                return str(cand)
    raise FileNotFoundError(f"Nu găsesc '{name}'. Instalați eclipse-sumo (pip) sau setați SUMO_HOME.")


def tool_path(relative: str) -> Path:
    """Calea unui script din SUMO_HOME/tools, de ex. tool_path('randomTrips.py')."""
    home = sumo_home()
    if not home:
        raise FileNotFoundError("SUMO_HOME necunoscut")
    return home / "tools" / relative


def write_e1_detectors(detectors, out_path, period_s: int = 60, output_file: str = "e1.xml") -> None:
    """detectors: listă de (id, lane_id, poziție_m). Scrie fișierul additional pentru SUMO."""
    root = ET.Element("additional")
    for det_id, lane, pos in detectors:
        ET.SubElement(root, "inductionLoop", id=str(det_id), lane=str(lane), pos=f"{pos:.1f}",
                      period=str(period_s), file=output_file)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)


def run_sumo(net, routes, additional=None, end_s: int = 3600, seed: int = 0, gui: bool = False,
             step_length: float = 1.0, on_step=None) -> None:
    """Rulează SUMO prin TraCI. `on_step(traci, t)` e apelat după fiecare pas (opțional)."""
    import traci

    cmd = [find_binary("sumo-gui" if gui else "sumo"), "-n", str(net), "-r", str(routes),
           "--seed", str(seed), "--step-length", str(step_length), "--end", str(end_s),
           "--no-step-log", "true", "--duration-log.disable", "true"]
    if additional:
        cmd += ["-a", str(additional)]
    traci.start(cmd)
    try:
        while traci.simulation.getTime() < end_s and traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            if on_step:
                on_step(traci, traci.simulation.getTime())
    finally:
        traci.close()


def read_e1_output(path) -> pd.DataFrame:
    """Citește ieșirea detectoarelor E1 (interval, id, flow [veh/h], speed [m/s], occupancy [%])."""
    rows = []
    for it in ET.parse(path).getroot().iter("interval"):
        rows.append({"begin": float(it.get("begin")), "end": float(it.get("end")), "id": it.get("id"),
                     "flow_veh_h": float(it.get("flow")), "speed_m_s": float(it.get("speed")),
                     "occupancy": float(it.get("occupancy")), "n_veh": int(float(it.get("nVehContrib")))})
    return pd.DataFrame(rows)
