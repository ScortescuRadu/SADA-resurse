"""Pune resursele temei voastre în repo-ul echipei.

    python instaleaza.py P3 ../repo_nostru              # instalează
    python instaleaza.py P3 ../repo_nostru --simulare   # doar arată ce ar face
    python instaleaza.py P3 ../repo_nostru --fara-config
    python instaleaza.py timisoara ../repo_nostru       # doar baza de date cu Timișoara (orice temă)
    python instaleaza.py vizualizare ../repo_nostru     # doar șabloanele de vizualizare (și baza)

Rulați-l din folderul de resurse, cu Python 3.10+ (merge și cu mediul din kit activat).
Ce face, în ordine:
  1. verifică că repo-ul e chiar al temei alese (config/default.yaml și src/sada/pN/);
  2. copiază fișierele din folderul temei (scripts/, src/, data/) la aceleași căi în repo;
     un fișier care există deja și e diferit se păstrează alături, cu sufixul .inainte_de_resurse;
  3. copiază comun/statistica_pereche.py în src/sada/, baza cu Timișoara în data/timisoara/
     și șabloanele de vizualizare în vizualizare/;
  4. adaugă în config/default.yaml secțiunile din config_de_adaugat.yaml (comentariile voastre
     rămân; vechiul fișier se păstrează ca config/default.yaml.inainte_de_resurse);
  5. adaugă proveniența datelor la sfârșitul lui data/DATA.md;
  6. rulează verifica.py pe repo.
Nu șterge nimic. Puteți rula scriptul de mai multe ori: fișierele identice sunt sărite.
"""
from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEME = {"P1": "P1_trafic", "P2": "P2_portofoliu", "P3": "P3_retea", "P4": "P4_transport"}
NU_SE_COPIAZA = {"README.md", "DATA.md", "config_de_adaugat.yaml"}
SUFIX = ".inainte_de_resurse"
MARCAJ = "<!-- resurse SADA: provenienta datelor -->"


class Jurnal:
    def __init__(self, simulare: bool):
        self.simulare = simulare
        self.n = {"copiat": 0, "identic": 0, "pastrat": 0}

    def __call__(self, msg):
        print(("[simulare] " if self.simulare else "") + msg)


# ---------------------------------------------------------------- copierea fișierelor
def copiaza(src: Path, dst: Path, log: Jurnal):
    if dst.exists():
        if filecmp.cmp(src, dst, shallow=False):
            log.n["identic"] += 1
            return
        backup = dst.with_name(dst.name + SUFIX)
        log(f"  {dst.relative_to(log.repo)} există și e diferit; vechiul rămâne ca {backup.name}")
        log.n["pastrat"] += 1
        if not log.simulare:
            shutil.copy2(dst, backup)
    else:
        log(f"  + {dst.relative_to(log.repo)}")
    log.n["copiat"] += 1
    if not log.simulare:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copiaza_tema(folder: Path, repo: Path, log: Jurnal):
    for f in sorted(folder.rglob("*")):
        if f.is_dir() or f.name in NU_SE_COPIAZA or "__pycache__" in f.parts or f.suffix == ".pyc":
            continue
        copiaza(f, repo / f.relative_to(folder), log)


def copiaza_baza(repo: Path, log: Jurnal):
    for nume in ("timisoara.sqlite", "timisoara.py"):
        copiaza(HERE / "comun/timisoara" / nume, repo / "data/timisoara" / nume, log)


def copiaza_vizualizare(repo: Path, log: Jurnal):
    src = HERE / "comun/vizualizare"
    for f in sorted(src.rglob("*")):
        if f.is_dir() or f.name == ".DS_Store" or "__pycache__" in f.parts:
            continue
        copiaza(f, repo / "vizualizare" / f.relative_to(src), log)


def copiaza_comun(repo: Path, log: Jurnal):
    copiaza(HERE / "comun/statistica_pereche.py", repo / "src/sada/statistica_pereche.py", log)
    copiaza_baza(repo, log)
    copiaza_vizualizare(repo, log)


# ---------------------------------------------------------------- config/default.yaml
TOP = re.compile(r"^([A-Za-z_][\w-]*):")
SUB = re.compile(r"^  ([A-Za-z_][\w-]*):")


def _blocuri(lines, start=0, end=None, nivel=TOP, indent=""):
    """{cheie: (început, sfârșit)} pentru cheile de pe un nivel. Comentariile lipite deasupra unei
    chei (fără linie goală între ele) fac parte din blocul ei."""
    end = len(lines) if end is None else end
    poz = [(i, nivel.match(lines[i]).group(1)) for i in range(start, end) if nivel.match(lines[i])]
    out = {}
    for k, (i, key) in enumerate(poz):
        s = i
        while s - 1 >= start and lines[s - 1].startswith(indent + "#"):
            s -= 1
        e = poz[k + 1][0] if k + 1 < len(poz) else end
        # la sfârșitul blocului: liniile goale și comentariile (ale cheii următoare sau ale nivelului
        # de deasupra) nu aparțin blocului acesta
        while e - 1 > i and (not lines[e - 1].strip() or lines[e - 1].lstrip().startswith("#")):
            e -= 1
        out[key] = (s, e)
    return out


def _sub_blocuri(lines, s, e):
    return _blocuri(lines, s + 1, e, SUB, "  ")


def combina_config(tinta: str, fragment: str) -> str:
    """Pune în textul `tinta` secțiunile și cheile din `fragment`, păstrând restul neatins."""
    fl = fragment.splitlines()
    for key, (fs, fe) in _blocuri(fl).items():
        tl = tinta.splitlines()
        tb = _blocuri(tl)
        if key not in tb:                                   # secțiune nouă: se adaugă la sfârșit
            tinta = tinta.rstrip("\n") + "\n\n" + "\n".join(fl[fs:fe]) + "\n"
            continue
        key_line = next(i for i in range(fs, fe) if TOP.match(fl[i]))
        for sub, (ss, se) in _sub_blocuri(fl, key_line, fe).items():
            tl = tinta.splitlines()
            ts, te = _blocuri(tl)[key]
            tkey = next(i for i in range(ts, te) if TOP.match(tl[i]))
            tsub = _sub_blocuri(tl, tkey, te)
            nou = fl[ss:se]
            if sub in tsub:                                  # cheie existentă: se înlocuiește
                a, b = tsub[sub]
                tl[a:b] = nou
            else:                                            # cheie nouă: la sfârșitul secțiunii
                tl[te:te] = nou
            tinta = "\n".join(tl) + "\n"
    return tinta


def _egal(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return all(k in b and _egal(v, b[k]) for k, v in a.items())
    return a == b


def actualizeaza_config(folder: Path, repo: Path, log: Jurnal):
    frag_path = folder / "config_de_adaugat.yaml"
    cfg_path = repo / "config/default.yaml"
    if not frag_path.exists():
        return
    vechi = cfg_path.read_text(encoding="utf-8")
    nou = combina_config(vechi, frag_path.read_text(encoding="utf-8"))
    try:
        import yaml
        f = yaml.safe_load(frag_path.read_text(encoding="utf-8"))
        n = yaml.safe_load(nou)
        if not _egal(f, n):
            raise ValueError("valorile din config_de_adaugat.yaml nu au ajuns toate în config")
    except ImportError:
        log("  (pyyaml lipsește: nu pot verifica config-ul rezultat; activați mediul din kit)")
    except Exception as e:                                   # noqa: BLE001
        sys.exit(f"Nu am modificat config/default.yaml: {e}. Adăugați secțiunile de mână din "
                 f"{frag_path.relative_to(HERE)}.")
    if nou == vechi:
        log("  config/default.yaml are deja tot ce trebuie")
        return
    log(f"  config/default.yaml: adăugate secțiunile din {frag_path.relative_to(HERE)} "
        f"(vechiul rămâne ca default.yaml{SUFIX})")
    if not log.simulare:
        shutil.copy2(cfg_path, cfg_path.with_name(cfg_path.name + SUFIX))
        cfg_path.write_text(nou, encoding="utf-8")


def actualizeaza_data_md(folder: Path, repo: Path, log: Jurnal):
    src = folder / "DATA.md"
    dst = repo / "data/DATA.md"
    if not src.exists():
        return
    text = dst.read_text(encoding="utf-8") if dst.exists() else "# DATA.md\n"
    if MARCAJ in text:
        return
    log("  data/DATA.md: adăugată proveniența datelor din resurse (completați data la care le-ați luat)")
    if not log.simulare:
        dst.parent.mkdir(parents=True, exist_ok=True)
        corp = src.read_text(encoding="utf-8").split("\n", 1)[1]
        dst.write_text(text.rstrip("\n") + f"\n\n{MARCAJ}\n## Date din resursele SADA\n{corp}", encoding="utf-8")


# ---------------------------------------------------------------- main
def verifica_repo(tema: str, repo: Path):
    if not (repo / "config/default.yaml").exists():
        sys.exit(f"{repo} nu pare un repo de proiect SADA: lipsește config/default.yaml.")
    if tema in TEME and not (repo / f"src/sada/{tema.lower()}").is_dir():
        alte = [t for t in TEME if (repo / f"src/sada/{t.lower()}").is_dir()]
        sys.exit(f"Repo-ul nu are src/sada/{tema.lower()}/" + (f"; pare să fie {alte[0]}." if alte else "."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tema", choices=[*TEME, "timisoara", "vizualizare"])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--simulare", action="store_true", help="arată ce s-ar face, fără să scrie nimic")
    ap.add_argument("--fara-config", action="store_true", help="nu atinge config/default.yaml")
    ap.add_argument("--fara-verificare", action="store_true")
    a = ap.parse_args()
    repo = a.repo.resolve()
    verifica_repo(a.tema, repo)
    log = Jurnal(a.simulare)
    log.repo = repo

    if a.tema == "timisoara":
        log(f"Baza cu Timișoara -> {repo}/data/timisoara/")
        copiaza_baza(repo, log)
    elif a.tema == "vizualizare":
        log(f"Șabloanele de vizualizare -> {repo}/vizualizare/")
        copiaza_baza(repo, log)
        copiaza_vizualizare(repo, log)
    else:
        folder = HERE / TEME[a.tema]
        log(f"Resursele {a.tema} -> {repo}")
        copiaza_tema(folder, repo, log)
        copiaza_comun(repo, log)
        if not a.fara_config:
            actualizeaza_config(folder, repo, log)
        actualizeaza_data_md(folder, repo, log)
    log(f"Gata: {log.n['copiat']} fișiere copiate, {log.n['identic']} deja identice, "
        f"{log.n['pastrat']} versiuni vechi păstrate cu sufixul {SUFIX}.")
    if a.tema in TEME and not a.simulare and not a.fara_verificare:
        print("\nVerificarea:", flush=True)
        r = subprocess.run([sys.executable, str(HERE / "verifica.py"), a.tema, str(repo)])
        if r.returncode == 0:
            print("\nVizualizarea: python -m http.server 8000 --directory vizualizare/sablon, apoi http://localhost:8000")
        sys.exit(r.returncode)
    if a.tema == "vizualizare" and not a.simulare:
        print("\nPorniți: python -m http.server 8000 --directory vizualizare/sablon, apoi http://localhost:8000"
              "\n(P1: http://localhost:8000/coridor.html). Instrucțiunile sunt în vizualizare/README.md.")


if __name__ == "__main__":
    main()
