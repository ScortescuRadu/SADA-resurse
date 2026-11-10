"""Descarcă feed-ul GTFS din Mobility Database și îl dezarhivează.

    python scripts/download_gtfs.py                 # feed-ul din config (gtfs.mdb_id)
    python scripts/download_gtfs.py --id mdb-2868

Pachetul disciplinei poate conține deja feed-ul sau un extras curățat (p4_gtfs/).
Dacă descărcarea automată nu merge, luați fișierul manual de pe pagina feed-ului:
    https://mobilitydatabase.org/feeds/gtfs/<id>
și puneți-l în data/raw/. Notați în data/DATA.md data descărcării: feed-ul se
actualizează, iar alt feed poate da alte rezultate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

from sada.config import load_config
from sada.p4.gtfs_io import feed_date_range, load_feed


def candidate_urls(mdb_id: str) -> list[str]:
    return [f"https://files.mobilitydatabase.org/{mdb_id}/{mdb_id}-latest.zip",
            f"https://files.mobilitydatabase.org/{mdb_id}/latest.zip"]


def main():
    cfg = load_config("config/default.yaml")["gtfs"]
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", default=cfg["mdb_id"])
    ap.add_argument("--url", help="URL direct către arhiva GTFS (sare peste Mobility Database)")
    a = ap.parse_args()
    raw = Path("data/raw")
    raw.mkdir(parents=True, exist_ok=True)
    zpath = raw / f"gtfs_{a.id}.zip"

    urls = [a.url] if a.url else candidate_urls(a.id)
    for url in urls:
        try:
            print(f"Descarc {url} ...")
            req = urllib.request.Request(url, headers={"User-Agent": "SADA-student-project"})
            with urllib.request.urlopen(req, timeout=120) as r, open(zpath, "wb") as f:
                shutil.copyfileobj(r, f)
            if not zipfile.is_zipfile(zpath):
                raise RuntimeError("fișierul descărcat nu e o arhivă zip")
            break
        except Exception as e:
            print(f"  eșec: {e}")
            zpath.unlink(missing_ok=True)
    else:
        sys.exit(f"Nu am putut descărca automat. Descărcați manual de pe "
                 f"https://mobilitydatabase.org/feeds/gtfs/{a.id} și puneți arhiva în {raw}/, "
                 f"apoi dezarhivați-o în {cfg['dir']}/.")

    out = Path(cfg["dir"])
    if out.exists():
        shutil.rmtree(out)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(out)
    # unele arhive au fișierele într-un subfolder
    inner = [p for p in out.iterdir() if p.is_dir()]
    if not (out / "stops.txt").exists() and len(inner) == 1:
        for p in inner[0].iterdir():
            shutil.move(str(p), out / p.name)
        inner[0].rmdir()

    feed = load_feed(out)
    rng = feed_date_range(feed)
    print(f"\nDezarhivat în {out}/: {len(feed['routes'])} linii, {len(feed['stops'])} stații, "
          f"{len(feed['trips'])} curse")
    if rng:
        print(f"Perioada de valabilitate: {rng[0]} – {rng[1]}")
    print(f"Pentru data/DATA.md: Mobility Database {a.id}, descărcat {dt.date.today().isoformat()}; "
          f"licența e cea indicată de operator pe pagina feed-ului.")
    print("Pasul următor: python scripts/inspect_gtfs.py")


if __name__ == "__main__":
    main()
