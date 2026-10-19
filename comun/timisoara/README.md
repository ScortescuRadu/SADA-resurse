# Datele despre Timișoara

Toate datele despre oraș din resurse, strânse într-un singur fișier SQLite (`timisoara.sqlite`, 0,6 MB), plus un modul Python care le citește (`timisoara.py`). Sunt aceleași date ca în folderele P2, P3 și P4, doar puse la un loc, ca să le puteți folosi și în altă temă, pentru o hartă sau pentru context în raport.

Instalare în repo (le pune în `data/timisoara/`):

```bash
python instaleaza.py timisoara ../repo_nostru
```

## Tabelele

| Tabel | Rânduri | Ce conține |
|---|---|---|
| `populatie` | 1134 | grila de 200 m: `x_m`, `y_m` (Stereo 70), `lat`, `lon`, `populatie`, `cartier` |
| `cartiere` | 34 | `cartier`, `populatie`, `acoperire_s0`, `acces_slab` (0/1), `geometrie_wkt` (poligon, WGS84) |
| `statii_linii` | 1112 | o linie pe (linie de transport, stație): coordonate, `headway_min` în vârful de dimineață, mod |
| `incarcari` | 120 | P4: `pasageri` pe linie (`route_id`) și `fereastra` de 15 min, 07:00–09:00 |
| `capacitati` | 3 | locuri pe vehicul, pe mod |
| `interventii` | 40 | P2: `tip`, `eticheta`, `cost_eur`, `beneficiu`, `echitate`, coordonate; `in_tm_A_20` |
| `interactiuni` | 54 | P2: perechile de intervenții suprapuse și beneficiul pierdut |
| `instante_p2` | 2 | P2: bugetul instanțelor `tm_A_40` și `tm_A_20` |
| `retea_noduri` | 1141 | P3: nodurile rețelei rutiere, cu `populatie` |
| `retea_muchii` | 2865 | P3: muchiile orientate, cu `lungime_m`, `timp_s`, `tip_drum`, `nume`, `importanta` |
| `scenarii_defect` | 150 | P3: muchiile căzute în fiecare `scenariu` și `faza` |
| `spitale` | 10 | P3: 9 spitale și gara, cu nodul cel mai apropiat din `retea_noduri` |
| `perechi_prioritare` | 36 | P3: perechile origine–destinație spre spitale |
| `surse` | 12 | de unde vine fiecare tabel și ce trebuie spus despre el în raport |

**Atenție la două lucruri:**
- **Ce e model.** `populatie`, `incarcari`, `beneficiu` și `echitate` sunt estimări de model, nu măsurători. Tabelul `surse` spune exact ce e fiecare.
- **Coordonatele.** `x_m`, `y_m` sunt în metri (EPSG:3844, Stereo 70), aceleași ca în `stops_xy` din kitul P4. `lat`, `lon` și geometriile sunt în WGS84.

## Din Python

```python
import sys
sys.path.insert(0, "data/timisoara")        # sau copiați timisoara.py în src/sada/
import timisoara as tm

tm.tabele()                                 # lista tabelelor, cu rândurile și sursa
pop = tm.populatie()                        # DataFrame
z = tm.cartiere(geometrie=True)             # GeoDataFrame (are nevoie de geopandas)
G = tm.retea()                              # networkx.MultiDiGraph, ca load_graph din P3
df = tm.sql("select * from interventii where tip = 'microbuz'")
```

Rulat direct, `python data/timisoara/timisoara.py` afișează lista tabelelor.

## Din SQL

Merge cu orice client SQLite (`sqlite3` din terminal, DB Browser for SQLite, extensia SQLite din VS Code).

```sql
-- cartierele fără acces bun la transport public, cu populația
select cartier, populatie, round(acoperire_s0 * 100) as acoperire_pct
from cartiere where acces_slab = 1 order by populatie desc;

-- câte linii trec prin fiecare stație (nodurile cele mai aglomerate)
select stop_name, count(distinct route_id) as linii
from statii_linii group by stop_name order by linii desc limit 10;

-- cele mai importante străzi din rețea
select nume, round(importanta, 3) as importanta, round(lungime_m) as m
from retea_muchii where nume is not null order by importanta desc limit 10;
```

## Cum s-a făcut

`fa_baza.py` construiește baza din fișierele din P2_portofoliu, P3_retea și P4_transport. Nu trebuie să-l rulați; e acolo ca să se vadă de unde vine fiecare tabel.
