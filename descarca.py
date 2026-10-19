"""Descarcă din nou sursele originale, dacă vreți să verificați de unde vin datele
sau să le refaceți de la zero. Pentru lucru nu aveți nevoie: totul e deja în folder.

    python descarca.py golly  ../repo_nostru/data/ca     # regulile și modelele Langton și Byl
    python descarca.py gtfs   ../repo_nostru/data/raw    # feed-ul GTFS STPT (mdb-2868), ultima versiune

golly: ia fișierele din oglinda GitHub a codului Golly și le compară cu cele din P3_retea/data/ca.
gtfs:  Mobility Database publică mereu ultima versiune a feed-ului. Ea poate diferi de cea din kit
       (2026-10-01 – 2026-12-31): orarul, liniile, ID-urile. Notați în data/DATA.md ce versiune folosiți.
Rețeaua, populația și cartierele nu se descarcă de aici: le refac scripturile build_* din fiecare
temă, din OpenStreetMap, și durează câteva minute.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLLY = "https://raw.githubusercontent.com/AlephAlpha/golly/master/"
GOLLY_FILES = {"Langtons-Loops.rule": "Rules/Langtons-Loops.rule", "Byl-Loop.rule": "Rules/Byl-Loop.rule",
               "Langtons-Loops.rle": "Patterns/Loops/Langtons-Loops.rle", "Byl-Loop.rle": "Patterns/Loops/Byl-Loop.rle"}
GTFS = ["https://files.mobilitydatabase.org/mdb-2868/mdb-2868-latest.zip",
        "https://files.mobilitydatabase.org/mdb-2868/latest.zip"]


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "sada-resurse/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def golly(dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for name, rel in GOLLY_FILES.items():
        data = get(GOLLY + rel)
        (dest / name).write_bytes(data)
        ref = HERE / "P3_retea/data/ca" / name
        same = ref.exists() and hashlib.sha256(ref.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()
        print(f"  {name}: {len(data)} octeți" + ("" if same else "  (diferă de copia din resurse: verificați)"))
    print(f"Salvat în {dest}. Citați Langton (1984), Byl (1989) și Golly ca sursă a fișierelor.")


def gtfs(dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for url in GTFS:
        try:
            data = get(url)
        except Exception as e:                            # noqa: BLE001
            print(f"  {url}: {e}")
            continue
        z = dest / "gtfs_mdb-2868.zip"
        z.write_bytes(data)
        with zipfile.ZipFile(z) as f:
            f.extractall(dest / "gtfs")
            info = f.read("feed_info.txt").decode("utf-8-sig").splitlines() if "feed_info.txt" in f.namelist() else []
        print(f"Salvat {z} și dezarhivat în {dest / 'gtfs'}")
        if len(info) > 1:
            print("  feed_info:", info[1])
        return
    sys.exit("Nu am putut descărca feed-ul. Luați-l manual de pe https://mobilitydatabase.org/feeds/gtfs/mdb-2868")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("golly", "gtfs"):
        sys.exit(__doc__)
    {"golly": golly, "gtfs": gtfs}[sys.argv[1]](Path(sys.argv[2]))
