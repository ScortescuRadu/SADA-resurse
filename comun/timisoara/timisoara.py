"""Datele despre Timișoara din timisoara.sqlite, gata de folosit.

    import timisoara as tm
    tm.tabele()                      # ce tabele sunt și de unde vine fiecare
    pop = tm.tabel("populatie")      # orice tabel, ca DataFrame
    tm.sql("select cartier, populatie from cartiere where acces_slab = 1")
    G = tm.retea()                   # rețeaua rutieră ca networkx.MultiDiGraph (ca load_graph din P3)
    z = tm.cartiere(geometrie=True)  # GeoDataFrame cu poligoanele (are nevoie de geopandas)

Puneți fișierul și timisoara.sqlite în același folder (de exemplu data/timisoara/) și adăugați
folderul în sys.path, sau copiați timisoara.py în src/sada/. Calea spre bază se poate da și
explicit: tm.BAZA = "cale/spre/timisoara.sqlite".

Merge doar cu biblioteca standard plus pandas; networkx și geopandas trebuie doar pentru
retea() și pentru geometrii.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

BAZA = Path(__file__).resolve().parent / "timisoara.sqlite"


def _con():
    if not Path(BAZA).exists():
        raise FileNotFoundError(f"Nu găsesc baza {BAZA}. Puneți timisoara.sqlite lângă timisoara.py "
                                f"sau setați timisoara.BAZA.")
    return sqlite3.connect(BAZA)


def sql(query: str, params=()) -> pd.DataFrame:
    """Rezultatul unei interogări SQL, ca DataFrame."""
    with _con() as con:
        return pd.read_sql_query(query, con, params=params)


def tabele() -> pd.DataFrame:
    """Tabelele din bază, cu numărul de rânduri și sursa fiecăruia."""
    with _con() as con:
        names = [r[0] for r in con.execute("select name from sqlite_master where type = 'table' order by name")]
        n = {t: con.execute(f'select count(*) from "{t}"').fetchone()[0] for t in names}
    surse = sql("select * from surse").set_index("tabel")
    return pd.DataFrame([{"tabel": t, "randuri": n[t], "sursa": surse["sursa"].get(t, ""), "nota": surse["nota"].get(t, "")}
                         for t in names])


def tabel(nume: str) -> pd.DataFrame:
    return sql(f'select * from "{nume}"')


def populatie() -> pd.DataFrame:
    """Grila de 200 m: x_m, y_m (Stereo 70, EPSG:3844), lat, lon, populatie, cartier."""
    return tabel("populatie")


def cartiere(geometrie: bool = False):
    """Cartierele: populație, acoperirea cu transport în S0, dacă au acces slab.
    Cu geometrie=True, un GeoDataFrame în WGS84 (EPSG:4326)."""
    df = tabel("cartiere")
    if not geometrie:
        return df.drop(columns="geometrie_wkt")
    import geopandas as gpd
    return gpd.GeoDataFrame(df.drop(columns="geometrie_wkt"), geometry=gpd.GeoSeries.from_wkt(df["geometrie_wkt"]),
                            crs=4326)


def statii() -> pd.DataFrame:
    """Stațiile liniilor urbane (un rând pe linie și stație), cu intervalul în vârful de dimineață."""
    return tabel("statii_linii")


def interventii(instanta: str = "tm_A_40") -> pd.DataFrame:
    """Intervențiile din portofoliul P2 (tm_A_40 sau tm_A_20)."""
    df = tabel("interventii")
    return df[df["in_tm_A_20"] == 1].reset_index(drop=True) if instanta == "tm_A_20" else df


def retea():
    """Rețeaua rutieră ca networkx.MultiDiGraph: noduri cu x (lon), y (lat), population;
    muchii cu length, travel_time, importance. Aceleași nume de atribute ca graful din P3."""
    import networkx as nx
    G = nx.MultiDiGraph()
    for r in tabel("retea_noduri").itertuples(index=False):
        G.add_node(r.node, x=r.lon, y=r.lat, population=r.populatie)
    for r in tabel("retea_muchii").itertuples(index=False):
        G.add_edge(r.u, r.v, key=r.key, length=r.lungime_m, travel_time=r.timp_s, highway=r.tip_drum,
                   name=r.nume, importance=r.importanta)
    return G


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    print(tabele()[["tabel", "randuri", "sursa"]].to_string(index=False))
