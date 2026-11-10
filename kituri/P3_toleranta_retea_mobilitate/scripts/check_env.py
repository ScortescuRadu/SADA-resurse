"""Verifică dacă mediul de lucru e pregătit: versiunea Python, pachetele,
programele externe și fișierele de date. Rulați-l după setup și ori de câte
ori ceva „nu merge pe calculatorul meu”.

    python scripts/check_env.py
"""
from __future__ import annotations

import importlib
import os
import shutil
import sys
from pathlib import Path

import yaml

OK, BAD, WARN = "  [ok]  ", "  [LIPSĂ]", "  [atenție]"


def find_binary(name: str) -> str | None:
    p = shutil.which(name)
    if p:
        return p
    home = os.environ.get("SUMO_HOME")
    if not home:
        try:
            import sumo  # pachetul eclipse-sumo
            home = sumo.SUMO_HOME
        except Exception:
            home = None
    if home:
        for cand in (Path(home) / "bin" / name, Path(home) / "bin" / f"{name}.exe"):
            if cand.exists():
                return str(cand)
    return None


def main():
    if not Path("config/default.yaml").exists():
        sys.exit("Nu găsesc config/default.yaml. Rulați scriptul din rădăcina proiectului.")
    cfg = yaml.safe_load(Path("config/default.yaml").read_text(encoding="utf-8"))
    env = cfg.get("env", {})
    problems = 0

    print("Python")
    v = sys.version_info
    if v >= (3, 10):
        print(f"{OK} {sys.version.split()[0]}")
    else:
        print(f"{BAD} {sys.version.split()[0]} (e nevoie de 3.10 sau mai nou)")
        problems += 1
    if sys.prefix == sys.base_prefix:
        print(f"{WARN} nu rulați într-un mediu virtual (.venv); vedeți docs/GIT_SI_MEDIU.md")

    print("Pachete")
    for mod in ["numpy", "scipy", "pandas", "matplotlib", "yaml", "sada"] + env.get("required_modules", []):
        try:
            m = importlib.import_module(mod)
            print(f"{OK} {mod} {getattr(m, '__version__', '')}")
        except Exception as e:
            print(f"{BAD} {mod}  ({e.__class__.__name__}: {e})")
            problems += 1

    if env.get("required_binaries"):
        print("Programe externe")
        for b in env["required_binaries"]:
            p = find_binary(b)
            print(f"{OK} {b}: {p}" if p else f"{BAD} {b} (vedeți README.md, secțiunea Instalare)")
            problems += 0 if p else 1

    if env.get("expected_files"):
        print("Date (pot lipsi la început; vedeți DATE.md)")
        for f in env["expected_files"]:
            print(f"{OK} {f}" if Path(f).exists() else f"{WARN} {f} nu există încă")

    print()
    print("Totul e în regulă." if problems == 0 else f"{problems} problemă/probleme de rezolvat (vedeți mai sus).")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
