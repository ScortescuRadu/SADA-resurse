"""Reface experimentul principal: toate scenariile × toate variantele × toate seed-urile.

    python scripts/run_all.py                                 # configurația implicită
    python scripts/run_all.py --config config/default.yaml
    python scripts/run_all.py --set experiment.n_runs=3       # test rapid

Funcția care simulează o rulare e indicată în config, la experiment.runner,
sub forma "modul:funcție". Rezultatele ajung în results/results.csv, iar
configurația folosită e copiată în results/config_used.yaml.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from sada.config import load_config, save_config
from sada.experiment import run_grid, seeds_from_config


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--set", nargs="*", default=[], help="suprascrieri cheie.subcheie=valoare")
    ap.add_argument("--out", default="results")
    args = ap.parse_args(argv)

    cfg = load_config(args.config, args.set)
    exp = cfg["experiment"]
    mod_name, fn_name = exp["runner"].split(":")
    run_one = getattr(importlib.import_module(mod_name), fn_name)

    scenarios = cfg.get("scenarios", {"default": {}})
    variants = cfg.get("variants", {"default": {}})
    # fiecare rulare primește și configurația globală, ca să nu o citiți din nou
    scenarios = {k: {**(v or {}), "_cfg": cfg} for k, v in scenarios.items()}

    out = Path(args.out)
    save_config(cfg, out / "config_used.yaml")
    try:
        df = run_grid(run_one, scenarios, variants, seeds_from_config(exp), out / "results.csv")
    except NotImplementedError as e:
        print(f"\nÎncă nu e implementat: {e}\nCompletați funcțiile marcate cu TODO (vedeți GHID.md).")
        sys.exit(1)
    print(f"\n{len(df)} rulări salvate în {out / 'results.csv'}")
    print("Pasul următor: python scripts/make_figures.py")


if __name__ == "__main__":
    main()
