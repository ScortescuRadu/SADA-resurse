"""Verifică resursele: că fișierele sunt întregi și că datele se încarcă cu codul din kit.

    python verifica.py                       # folderul de resurse: sumele de control ale tuturor fișierelor
    python verifica.py P3 ../repo_nostru   # după instalare: fișierele, config-ul și încărcarea datelor

Rulați a doua formă cu mediul din kit activat (source .venv/bin/activate), pentru că
verificarea importă pachetul sada al repo-ului vostru.
Codul de ieșire e 0 dacă totul e în regulă și 1 dacă ceva lipsește sau nu se potrivește.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "MANIFEST.json"
TEME = {"P1": "P1_trafic", "P2": "P2_portofoliu", "P3": "P3_retea", "P4": "P4_transport"}
OK, BAD, WARN = "  [ok]     ", "  [PROBLEMĂ]", "  [atenție]"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def toate_fisierele():
    for f in sorted(HERE.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts and ".git" not in f.relative_to(HERE).parts and f.name not in ("MANIFEST.json", ".DS_Store", ".gitignore") \
                and f.suffix != ".pyc" and not f.name.endswith(".inainte_de_resurse"):
            yield f


def refa_manifest():
    MANIFEST.write_text(json.dumps({str(f.relative_to(HERE)): sha(f) for f in toate_fisierele()}, indent=1),
                        encoding="utf-8")
    print(f"Scris {MANIFEST}")


class Raport:
    def __init__(self):
        self.probleme = 0

    def ok(self, msg):
        print(OK, msg)

    def bad(self, msg, cum=None):
        self.probleme += 1
        print(BAD, msg)
        if cum:
            print("              ->", cum)

    def warn(self, msg):
        print(WARN, msg)

    def check(self, cond, msg, cum=None):
        (self.ok(msg) if cond else self.bad(msg, cum))


def verifica_folderul(r: Raport):
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for rel, h in man.items():
        f = HERE / rel
        if not f.exists():
            r.bad(f"lipsește {rel}", "descărcați din nou folderul de resurse")
        elif sha(f) != h:
            r.bad(f"{rel} diferă de versiunea distribuită", "dacă nu l-ați modificat voi, descărcați-l din nou")
    if not r.probleme:
        r.ok(f"toate cele {len(man)} fișiere sunt întregi")


def verifica_fisierele_din_repo(tema, repo: Path, r: Raport):
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pref = TEME[tema] + "/"
    for rel, h in man.items():
        if not rel.startswith(pref) or Path(rel).name in ("README.md", "DATA.md", "config_de_adaugat.yaml"):
            continue
        dst = repo / rel[len(pref):]
        if not dst.exists():
            r.bad(f"lipsește {dst.relative_to(repo)}", f"python instaleaza.py {tema} {repo}")
        elif sha(dst) != h:
            if dst.suffix == ".py":
                r.warn(f"{dst.relative_to(repo)} e modificat față de resurse (în regulă dacă l-ați schimbat voi)")
            else:
                r.bad(f"{dst.relative_to(repo)} diferă de datele din resurse",
                      "dacă le-ați refăcut voi cu scriptul, e în regulă; altfel reinstalați")
    for nume in ("timisoara.sqlite", "timisoara.py"):
        if not (repo / "data/timisoara" / nume).exists():
            r.warn(f"data/timisoara/{nume} lipsește (opțional: python instaleaza.py timisoara {repo})")


def incarca_config(repo):
    import yaml
    return yaml.safe_load((repo / "config/default.yaml").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- verificări pe teme
def p1(repo, cfg, r):
    from sada.p1.sumo_tools import find_binary
    for b in ("sumo", "netconvert"):
        try:
            r.ok(f"{b}: {find_binary(b)}")
        except Exception as e:                       # noqa: BLE001
            r.bad(f"nu găsesc {b} ({e})", "pip install eclipse-sumo sau setați SUMO_HOME")
    m = cfg.get("model", {})
    lipsa = [k for k in ("length_m", "segment_m", "lanes", "cell_m", "vmax", "dt_s", "warmup_s", "duration_s") if k not in m]
    r.check(not lipsa, "config: secțiunea model are cheile de care are nevoie sumo_coridor_drept.py",
            f"lipsesc: {lipsa}")


def p2(repo, cfg, r):
    from sada.p2.exact import solve
    from sada.p2.problem import Problem
    p = Problem.from_json(repo / "data/p2_portofoliu/tm_A_40.json")
    r.check(p.n == 40 and getattr(p, "has_interactions", False),
            f"tm_A_40: {p.n} intervenții, cu interacțiuni", "problem.py din resurse nu e instalat (sau a fost suprascris)")
    x, v = solve(p)
    r.check(abs(v - 377.49) < 0.01, f"optimul exact al stării inițiale: {v:.2f} (așteptat 377,49)",
            "exact.py din resurse nu e instalat sau datele diferă")
    sc = cfg.get("scenarios", {})
    for k in ("tm_A_20", "tm_A_40"):
        r.check(k in sc and Path(repo, sc[k]["instance"]).exists(), f"config: scenariul {k}",
                "lipsește din config/default.yaml; vedeți config_de_adaugat.yaml")
    if not Path(repo, "results/optima_tm_A_40.json").exists():
        r.warn("optimele nu sunt calculate încă: python scripts/solve_optima.py data/p2_portofoliu/tm_A_40.json "
               "data/p2_portofoliu/changes_tm_A_40.json")


def p3(repo, cfg, r):
    from sada.p3.graph_io import load_graph, summarize
    G = load_graph(repo / cfg["data"]["graph"])
    s = summarize(G)
    r.check(s["nodes"] == 1141 and s["edges"] == 2865 and s["components"] == 1,
            f"graful din config: {s['nodes']} noduri, {s['edges']} muchii, {s['components']} componentă tare conexă",
            "data.graph din config trebuie să fie data/p3_retea/retea.graphml")
    pop = sum(float(d.get("population", 0)) for _, d in G.nodes(data=True))
    r.check(pop > 1e5, f"populația pe noduri: {pop:,.0f} locuitori (estimare)")
    scen = json.loads((repo / cfg["data"]["group_scenarios"]).read_text(encoding="utf-8"))
    grupuri = [v.get("group") for v in cfg.get("scenarios", {}).values() if v and v.get("failure") == "group"]
    r.check(all(g in scen for g in grupuri), f"scenariile în grup din config există în fișier: {grupuri}")
    r.check(Path(repo, cfg["od"].get("priority_file") or "").is_file(), "od.priority_file indică prioritare.csv",
            "puneți od.priority_file: data/p3_retea/prioritare.csv")
    from sada.p3.verificare_golly import verify_against_tree
    for rule in ("Langtons-Loops", "Byl-Loop"):
        v = verify_against_tree(repo / f"data/ca/{rule}.rule")
        r.check(v["identical"], f"{rule}: tabelul citit = arborele Golly pe {v['neighbourhoods']} vecinătăți")


def p4(repo, cfg, r):
    import pandas as pd
    loads = pd.read_csv(repo / cfg["data"]["loads"])
    r.check(len(loads) == 120 and loads["window"].nunique() == 8, f"încărcări: {loads.route_id.nunique()} linii × 8 ferestre")
    routes = pd.read_csv(repo / cfg["gtfs"]["dir"] / "routes.txt", dtype=str)
    alese = routes[routes.route_short_name.isin([str(x) for x in cfg["gtfs"].get("routes", [])])].route_id
    lipsa = sorted(set(alese) - set(loads.route_id))
    r.check(alese.size > 0 and not lipsa, f"toate cele {alese.size} linii din gtfs.routes au încărcări",
            f"fără încărcări: {lipsa}; ori folosiți liniile din config_de_adaugat.yaml, ori rulați scripts/build_dataset.py")
    pop = pd.read_csv(repo / cfg["data"]["population"])
    r.check(abs(pop.population.sum() - 315391) < 1, f"populația: {pop.population.sum():,.0f} locuitori pe {len(pop)} celule")
    for k in ("capacities", "weak_zones", "zones", "stop_routes"):
        r.check(Path(repo, cfg["data"].get(k, "")).is_file(), f"config: data.{k}")
    from sada.p4.layover import measured_layover  # noqa: F401
    r.ok("sada.p4.layover se importă")
    s0p = Path(repo, cfg["data"]["s0"])
    if not s0p.exists():
        r.warn("data/s0.csv lipsește: python scripts/baseline_s0.py")
    elif set(pd.read_csv(s0p).route_id) != set(alese):
        r.warn("data/s0.csv nu conține exact liniile din gtfs.routes (cel din kit e pentru toate liniile): "
               "python scripts/baseline_s0.py")


def main():
    r = Raport()
    if len(sys.argv) >= 2 and sys.argv[1] == "--refa-manifest":
        return refa_manifest()
    if len(sys.argv) == 1:
        print("Folderul de resurse:")
        verifica_folderul(r)
        sys.exit(1 if r.probleme else 0)
    if len(sys.argv) != 3 or sys.argv[1] not in TEME:
        sys.exit(__doc__)
    tema, repo = sys.argv[1], Path(sys.argv[2]).resolve()
    print(f"Fișierele {tema} în {repo}:")
    verifica_fisierele_din_repo(tema, repo, r)
    print("Config și date:")
    sys.path.insert(0, str(repo / "src"))
    os.chdir(repo)
    try:
        cfg = incarca_config(repo)
        {"P1": p1, "P2": p2, "P3": p3, "P4": p4}[tema](repo, cfg, r)
    except ModuleNotFoundError as e:
        r.bad(f"lipsește un modul: {e.name}", "activați mediul din kit (source .venv/bin/activate) și reîncercați")
    except Exception as e:                           # noqa: BLE001
        r.bad(f"{e.__class__.__name__}: {e}")
    print("\n" + ("Totul e în regulă." if not r.probleme else f"{r.probleme} probleme; vedeți mai sus."))
    sys.exit(1 if r.probleme else 0)


if __name__ == "__main__":
    main()
