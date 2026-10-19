# Proveniența datelor (de copiat în data/DATA.md)

| Fișier | Sursă | Obținut la | Licență | Prelucrări |
|---|---|---|---|---|
| `raw/gtfs/*.txt`, `raw/gtfs_mdb-2868.zip` | GTFS STPT / SMTT Timișoara, Mobility Database **mdb-2868** (`scripts/download_gtfs.py`); feed versiunea 4.26, valabil 2026-10-01 – 2026-12-31 | din kit (2026-10-06) | licența operatorului (SMTT), vezi pagina feed-ului în Mobility Database | niciuna; ziua folosită: miercuri 2026-10-14 |
| `p4_gtfs/populatie_grila.csv` | OpenStreetMap (clădiri), prin OSMnx (`scripts/build_dataset.py`), raza 6,5 km în jurul Pieței Victoriei | 2026-10-14 | ODbL, © OpenStreetMap contributors | **model**: suprafața desfășurată a clădirilor rezidențiale / 30 m² pe locuitor, agregată pe o grilă de 200 m (Stereo 70); ~315 000 de locuitori |
| `p4_gtfs/zone.geojson` | OSM `place=suburb/quarter/neighbourhood` | 2026-10-14 | ODbL | celule Voronoi pe grila de populație; 34 de cartiere cu ≥ 1500 de locuitori; acoperirea S0 pe cartier |
| `p4_gtfs/zone_acces_slab.geojson` | derivat | 2026-10-14 | ODbL (derivat) | cele 6 cartiere cu cea mai mică acoperire în S0 (Europa, Planetelor, Braytim–Timișoara Sud, Cvartal UMT, Cora, Fratelia) |
| `p4_gtfs/statii_linii.csv` | derivat din GTFS | 2026-10-14 | ca GTFS | stațiile celor 39 de linii urbane cu cel puțin 4 curse în fereastră și intervalul lor în S0 (pentru acoperire) |
| `p4_gtfs/capacitati.csv` | ipoteze (fișe tehnice tipice) | 2026-10-14 | – | tramvai 180, troleibuz 100, autobuz 100 de locuri (șezut + în picioare) |
| `p4_gtfs/incarcari.csv` | **model de cerere** (`scripts/build_dataset.py`, `demand_model`) | 2026-10-14 | – | pasagerii în secțiunea de vârf, pe linie și fereastră de 15 min; generare din populație la ≤ 400 m de stații, împărțire pe linii după frecvență, factor de trecere prin secțiunea de vârf, atractivitate lognormală (σ = 0,25, seed 4), profil de vârf; calibrat la gradul de încărcare mediu 0,70 la vârf în S0 |

Note:
- **Încărcările nu sunt validări de bilete și nici măsurători.** Vin dintr-un model de cerere (descris în `scripts/build_dataset.py`, funcția `demand_model`), calibrat astfel încât gradul de încărcare mediu la vârf în S0 să fie 0,70. Populația e și ea o estimare.
- Încărcările sunt pentru cele 15 linii din `config_de_adaugat.yaml`. Pentru alte linii, refaceți `data/s0.csv` și rulați `scripts/build_dataset.py`.
- Capacitățile sunt ipoteze de ordin de mărime; dacă găsiți valori mai bune pentru flota STPT, folosiți-le și spuneți sursa.
