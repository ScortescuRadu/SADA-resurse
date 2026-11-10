"""Citirea fișierului de configurare (YAML) cu suprascrieri din linia de comandă.

Exemplu:
    cfg = load_config("config/default.yaml", overrides=["experiment.n_runs=5"])
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml


def _parse_value(text: str):
    """Transformă '5' în 5, '0.3' în 0.3, 'true' în True; restul rămân text."""
    return yaml.safe_load(text)


def _set_path(d: dict, dotted: str, value) -> None:
    keys = dotted.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def load_config(path: str | Path, overrides: list[str] | None = None) -> dict:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Nu găsesc {path}. Rulați scripturile din rădăcina proiectului (folderul care conține "
            f"README.md și config/), de exemplu: python scripts/run_all.py")
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg = copy.deepcopy(cfg)
    for item in overrides or []:
        if "=" not in item:
            raise ValueError(f"Suprascrierea trebuie să aibă forma cheie.subcheie=valoare, nu '{item}'")
        key, val = item.split("=", 1)
        _set_path(cfg, key.strip(), _parse_value(val))
    return cfg


def save_config(cfg: dict, path: str | Path) -> None:
    """Salvați configurația folosită lângă rezultate, ca să știți mereu ce a produs un fișier."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
