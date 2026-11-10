"""Verifică dacă sunteți pregătiți pentru o etapă a proiectului.

    python scripts/milestone_check.py            # lista etapelor
    python scripts/milestone_check.py M3         # verificările pentru prototip

Verificările sunt în milestones/checks.yaml. Fiecare are un indiciu despre ce
trebuie făcut dacă nu trece. Scriptul nu vă dă nota; vă spune doar ce lipsește.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

OK, FAIL = "  [✔]", "  [✘]"


def get(cfg, dotted):
    for k in dotted.split("."):
        if not isinstance(cfg, dict) or k not in cfg:
            return None
        cfg = cfg[k]
    return cfg


def run_check(c, cfg) -> tuple[bool, str]:
    kind = c["type"]
    if kind == "file":
        return Path(c["path"]).exists(), c["path"]
    if kind == "nonempty_dir":
        p = Path(c["path"])
        return p.is_dir() and any(x for x in p.iterdir() if not x.name.startswith(".")), c["path"]
    if kind == "config_set":
        v = get(cfg, c["key"])
        bad = v is None or v == [] or (isinstance(v, str) and "TODO" in v)
        return not bad, f"config: {c['key']} = {v!r}"
    if kind == "text_absent":
        p = Path(c["path"])
        return p.exists() and not re.search(c["pattern"], p.read_text(encoding="utf-8")), f"{c['path']} fără „{c['pattern']}”"
    if kind == "text_present":
        p = Path(c["path"])
        return p.exists() and re.search(c["pattern"], p.read_text(encoding="utf-8")) is not None, f"{c['path']} conține „{c['pattern']}”"
    if kind == "pytest":
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rs", *c["args"]], capture_output=True, text=True)
        out = r.stdout.strip().splitlines()
        summary = out[-1] if out else "?"
        return r.returncode == 0 and "skipped" not in summary, f"pytest {' '.join(c['args'])}: {summary}"
    if kind == "command":
        r = subprocess.run([sys.executable, *c["args"]], capture_output=True, text=True, timeout=c.get("timeout", 600))
        return r.returncode == 0, "python " + " ".join(c["args"])
    raise ValueError(f"tip de verificare necunoscut: {kind}")


def main():
    spec = yaml.safe_load(Path("milestones/checks.yaml").read_text(encoding="utf-8"))
    if len(sys.argv) < 2 or sys.argv[1] not in spec:
        print("Etape disponibile:")
        for k, v in spec.items():
            print(f"  {k}: {v['title']}")
        return
    m = spec[sys.argv[1]]
    cfg = yaml.safe_load(Path("config/default.yaml").read_text(encoding="utf-8"))
    print(f"{sys.argv[1]}: {m['title']}\n")
    failed = 0
    for c in m["checks"]:
        try:
            ok, what = run_check(c, cfg)
        except Exception as e:  # o verificare stricată nu oprește restul
            ok, what = False, f"eroare la verificare: {e}"
        print(f"{OK if ok else FAIL} {c['name']}  ({what})")
        if not ok:
            failed += 1
            print(f"        -> {c['hint']}")
    print(f"\n{len(m['checks']) - failed}/{len(m['checks'])} verificări trecute.")
    print(f"Detalii: {m['doc']}")


if __name__ == "__main__":
    main()
