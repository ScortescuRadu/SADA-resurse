#!/usr/bin/env bash
# Instalează mediul de lucru pe Linux / macOS / WSL.
#   bash setup/setup.sh
# Folosiți alt interpretor cu:  PYTHON=python3.12 bash setup/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Nu găsesc $PY. Instalați Python 3.10+ (https://www.python.org/downloads/)." >&2
  exit 1
fi
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || { echo "E nevoie de Python 3.10 sau mai nou. Aveți: $("$PY" --version)" >&2; exit 1; }

if [ ! -d .venv ]; then
  echo ">> Creez mediul virtual .venv"
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo ">> Instalez dependențele (poate dura câteva minute)"
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
python -m pip install -e .          # pachetul `sada` din src/, în mod editabil

echo ">> Verific mediul"
python scripts/check_env.py || true

cat <<'MSG'

Gata. De fiecare dată când deschideți un terminal nou, activați mediul:
    source .venv/bin/activate
Apoi încercați exemplul:
    python examples/toy_mapek.py
MSG
