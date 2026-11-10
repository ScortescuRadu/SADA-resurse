"""Verificarea finală înainte de predare (etapa M5). Face, pe o copie curată a
depozitului, ce va face și cadrul didactic: rulează testele
și un experiment scurt, apoi caută problemele uzuale (date fără sursă, chei de
acces, fișiere lipsă).

    python scripts/verify_submission.py           # complet
    python scripts/verify_submission.py --fast    # fără experimentul scurt

Copia curată se face cu `git clone` (deci doar ce e comis contează).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SECRET = re.compile(r"(api[_-]?key|secret|password|parola|token)\s*[:=]\s*['\"][^'\"]{8,}", re.I)
REQUIRED = ["README.md", "requirements.txt", "config/default.yaml", "data/DATA.md", "scripts/run_all.py",
            "scripts/make_figures.py"]


def step(msg):
    print(f"\n== {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    problems = []

    step("Starea depozitului")
    if subprocess.run(["git", "rev-parse"], capture_output=True).returncode != 0:
        raise SystemExit("Nu e un depozit Git. Vedeți docs/GIT_SI_MEDIU.md.")
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if dirty:
        problems.append("există modificări necomise (git status); copia curată nu le va conține")
        print(dirty)

    tmp = Path(tempfile.mkdtemp(prefix="sada_verify_"))
    step(f"Clonez într-un folder curat: {tmp}")
    subprocess.run(["git", "clone", "-q", ".", str(tmp / "repo")], check=True)
    repo = tmp / "repo"

    step("Fișiere obligatorii")
    for f in REQUIRED:
        ok = (repo / f).exists()
        print(f"  {'[✔]' if ok else '[✘]'} {f}")
        if not ok:
            problems.append(f"lipsește {f}")
    if not (repo / "requirements.lock.txt").exists():
        problems.append("lipsește requirements.lock.txt (pip freeze > requirements.lock.txt)")
    data_md = (repo / "data/DATA.md").read_text(encoding="utf-8") if (repo / "data/DATA.md").exists() else ""
    if "exemplu.csv" in data_md:
        problems.append("data/DATA.md mai conține rândul de exemplu; completați-l cu fișierele reale")

    step("Căutare de chei și parole")
    for p in repo.rglob("*"):
        if p.is_file() and p.suffix in {".py", ".yaml", ".yml", ".md", ".json", ".txt", ".ipynb", ".cfg", ".env"}:
            if ".git" in p.parts:
                continue
            if SECRET.search(p.read_text(encoding="utf-8", errors="ignore")):
                problems.append(f"posibilă cheie sau parolă în {p.relative_to(repo)}")

    step("Teste în copia curată")
    # codul din copie are prioritate față de cel instalat (fără să atingem mediul vostru .venv)
    env = {**os.environ, "PYTHONPATH": str(repo / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, capture_output=True, text=True, env=env)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
    if r.returncode:
        problems.append("testele nu trec în copia curată")
    elif "skipped" in r.stdout:
        problems.append("unele teste sunt sărite: la predare, părțile TODO ar trebui să fie implementate")

    if not a.fast:
        step("Experiment scurt (2 rulări) și figuri, în copia curată")
        r = subprocess.run([sys.executable, "scripts/run_all.py", "--set", "experiment.n_runs=2"], cwd=repo,
                           capture_output=True, text=True, env=env)
        if r.returncode:
            problems.append("scripts/run_all.py eșuează în copia curată (părți TODO neimplementate sau date care nu sunt în depozit?)")
            print(r.stdout[-800:], r.stderr[-800:])
        else:
            r = subprocess.run([sys.executable, "scripts/make_figures.py"], cwd=repo, capture_output=True, text=True, env=env)
            if r.returncode:
                problems.append("scripts/make_figures.py eșuează în copia curată")

    shutil.rmtree(tmp, ignore_errors=True)
    step("Rezultat")
    if problems:
        for p in problems:
            print(f"  - {p}")
        print(f"\n{len(problems)} problemă/probleme de rezolvat înainte de predare.")
        sys.exit(1)
    print("Totul e în regulă. Mai rămân raportul (PDF) și prezentarea; vedeți raport/CHECKLIST.md.")


if __name__ == "__main__":
    main()
