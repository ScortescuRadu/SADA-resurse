# P4. Frecvența transportului public: resurse

## Pe scurt

Primiți datele care lipseau din pachetul `p4_gtfs/`:
- încărcările pe linie și fereastră de 15 minute (dintr-un model de cerere);
- capacitățile vehiculelor;
- populația, cartierele și cele cu acces slab la transport;
- stațiile tuturor liniilor urbane.

Primiți și o funcție care măsoară din GTFS timpul real de întoarcere la capăt, în locul celor 5 minute presupuse în kit.

## Instalare

Din folderul de resurse, cu mediul din kit activat:

```bash
python instaleaza.py P4 ../repo_nostru
```

Ce apare în repo:

| Fișier | La ce folosește |
|---|---|
| `data/p4_gtfs/incarcari.csv` | pasagerii în secțiunea de vârf: `route_id, window, start, passengers` (15 linii × 8 ferestre, 07:00–09:00) |
| `data/p4_gtfs/capacitati.csv` | locuri pe vehicul: tramvai 180, troleibuz 100, autobuz 100 |
| `data/p4_gtfs/populatie_grila.csv` | populația pe o grilă de 200 m: `x_m, y_m` (Stereo 70, ca `stops_xy`), `lat, lon, population, zone` |
| `data/p4_gtfs/zone.geojson` | 34 de cartiere, cu populația și acoperirea în S0 |
| `data/p4_gtfs/zone_acces_slab.geojson` | cele 6 cartiere cu cea mai slabă acoperire |
| `data/p4_gtfs/statii_linii.csv` | stațiile celor 39 de linii urbane și intervalul lor în vârf |
| `src/sada/p4/layover.py` | `measured_layover`: întoarcerea la capăt, din `block_id` |
| `scripts/build_dataset.py` | reface `data/p4_gtfs/` (doar dacă alegeți alte linii) |

În `config/default.yaml` se schimbă:
- `gtfs.routes`: cele 15 linii pentru care sunt calculate încărcările (tramvaiele 1, 2, 7, 9; troleibuzele 11, 14, 15, 17; autobuzele 13, 21, 33, 40, 5c, E1, E7);
- secțiunea `data`: căile către fișierele de mai sus, plus `zones`, `population` și `stop_routes`;
- secțiunea nouă `dataset`, cu parametrii pentru `build_dataset.py`.

## Primii pași

**1. Refaceți orarul S0 pentru liniile alese.** `data/s0.csv` din kit e calculat pentru toate liniile:

```bash
python scripts/baseline_s0.py
```

**2. Verificați instalarea:**

```bash
python ../SADA_resurse_studenti/verifica.py P4 .
```

Trebuie să vedeți `toate cele 15 linii din gtfs.routes au încărcări` și nicio `[PROBLEMĂ]`.

**3. Uitați-vă la încărcări înainte să scrieți controllerul.** Gradul de încărcare la vârf, pe linie:

```python
import pandas as pd
s0 = pd.read_csv("data/s0.csv").groupby("route_id").agg(n=("n_trips", "mean"), mode=("mode", "first"))
cap = pd.read_csv("data/p4_gtfs/capacitati.csv").set_index("mode").capacity
L = pd.read_csv("data/p4_gtfs/incarcari.csv").groupby("route_id").passengers.max()
oferit = s0.n / 8 * s0["mode"].map(cap)          # locuri pe sens într-o fereastră de 15 minute
print((L / oferit).sort_values().round(2))
```

Unele linii ies sub 0,30, altele peste 0,85. Asta îi dă controllerului ce să realoce.

## Ce înseamnă coloanele din incarcari.csv

`passengers` = numărul de pasageri din **secțiunea cea mai încărcată** a liniei, în **sensul cel mai încărcat**, într-o fereastră de 15 minute. Se compară cu capacitatea oferită pe sens în aceeași fereastră: curse pe sens × locuri pe vehicul. `window` e 0 pentru 07:00, 1 pentru 07:15 … 7 pentru 08:45.

Modelul de cerere (`build_dataset.py`, funcția `demand_model`), pe scurt:

1. Populația de lângă fiecare stație se împarte între liniile care o deservesc, după frecvență.
2. Doar o parte din cei îmbarcați se află în secțiunea de vârf; pe liniile lungi, mai puțini.
3. Un factor aleator de atractivitate pe linie acoperă ce nu prinde populația rezidențială (universități, mall-uri).
4. Profilul de vârf al dimineții distribuie cererea pe ferestre.
5. Totul e calibrat astfel încât gradul de încărcare mediu la vârf în S0 să fie 0,70.

**Nu sunt validări de bilete**; scrieți asta în raport.

## Întoarcerea la capăt

Feed-ul STPT are `block_id`: știm ce curse face același vehicul, una după alta. Timpul dintre sosirea unei curse și plecarea următoarei e timpul real la capăt. Pe liniile alese iese între 1 și 10 minute (mediana pe rețea, 6), deci cele 5 minute presupuse în kit subestimează unele linii și le supraestimează pe altele.

```python
from sada.p4.gtfs_io import load_feed, active_service_ids
from sada.p4.layover import measured_layover
feed = load_feed("data/raw/gtfs")
sids = active_service_ids(feed, "2026-10-14")
lay = measured_layover(feed, sids, "07:00:00", "09:00:00")   # {route_id: minute}
```

Ca să-l folosiți în S0:
1. În `src/sada/p4/baseline.py`, în `vehicle_hours`, faceți ca `layover_min` să poată fi și un dicționar pe linie.
2. În `scripts/baseline_s0.py`, dați rezultatul lui `measured_layover` în loc de numărul din config.
3. Spuneți în raport ce valori ați folosit.

## Acoperirea

Pentru metrica de acoperire aveți nevoie de două lucruri pe care kitul nu le dă: punctele de populație (`populatie_grila.csv`) și stațiile **tuturor** liniilor urbane (`statii_linii.csv`). O stație e bine deservită dacă trece pe acolo orice linie cu interval ≤ 20 de minute, nu doar una dintre cele 15 pe care le controlați. Liniile pe care nu le controlați rămân cu intervalul din `headway_min`. Coordonatele `x_m`, `y_m` sunt deja în Stereo 70, ca `stops_xy(feed)`.

## Ce aveți de făcut

Tot ce e marcat TODO în kit:

- [ ] `TransitSystem.from_files` (pasul 3 din GHID): formatul de mai sus e unul posibil; dacă vă iese mai simplu altfel, schimbați-l și spuneți;
- [ ] `SimpleRuleController` și `GAController`, cu `ga_alloc.allocate`;
- [ ] `coverage_share` în `coverage.py`;
- [ ] `run_one`: perturbările (închiderea unei linii, +20% cerere într-o zonă) și experimentele;
- [ ] vizualizarea: vehiculele pe hartă, colorate după gradul de încărcare, din cursele voastre. Exportul din GTFS e în `vizualizare/README.md`, secțiunea P4.

## La ce să vă așteptați

- **Ordinea din demonstrația kitului e greșită.** `demo_prototip.py` apelează controllerul înainte să calculeze încărcarea ferestrei, adică îi arată cererea înainte s-o servească. În experimente, ordinea corectă e: fereastra se servește cu cursele alese înainte, apoi controllerul vede încărcarea și decide pentru fereastra următoare.
- **Un tramvai nu poate circula pe o linie de autobuz.** Gândiți-vă dacă bugetul de ore-vehicul trebuie respectat global sau pe fiecare mod, și justificați alegerea.
- **Încărcările au extreme.** Două linii rare prin cartiere dense (13 și E1) sunt mult peste 100% la vârf. Limita pe care o puneți pe numărul maxim de curse pe linie contează mult.
- **Ponderea curselor supraaglomerate** (metrica din fișă) poate crește chiar când controllerul face lucrurile bine: dacă adăugați curse pe o linie care rămâne peste 100%, adăugați curse supraaglomerate. Raportați și pasagerii peste capacitate, ca să vedeți diferența.
- **Nu toate cartierele cu acces slab sunt pe liniile alese.** Verificați pe care le puteți influența prin frecvență înainte să trageți concluzii despre acoperire.

## Întrebări frecvente

**Vreau alte linii.**
1. Schimbați `gtfs.routes`.
2. Rulați `python scripts/baseline_s0.py`.
3. Instalați `pip install osmnx geopandas`.
4. Rulați `python scripts/build_dataset.py`, care reface toate fișierele din `data/p4_gtfs/` pentru liniile voastre, cu internet, în câteva minute.

**Pot schimba calibrarea cererii?** Da, `dataset.target_peak_load` și celelalte din secțiunea `dataset`. Rulați din nou `build_dataset.py` și spuneți în raport ce ați schimbat.

**Feed-ul GTFS s-a schimbat.** Kitul vine cu versiunea valabilă 2026-10-01 – 2026-12-31. Dacă descărcați alta, ID-urile liniilor pot diferi și încărcările trebuie refăcute.
