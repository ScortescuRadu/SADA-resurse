# Proveniența datelor (de copiat în data/DATA.md)

| Fișier | Sursă | Obținut la | Licență | Prelucrări |
|---|---|---|---|---|
| `p3_retea/retea.graphml` | OpenStreetMap prin OSMnx 2.1 (`scripts/build_dataset.py`), rețeaua `drive`, raza 2500 m în jurul (45.7537, 21.2257), Piața Victoriei, Timișoara | 2026-10-14 | ODbL, © OpenStreetMap contributors | intersecții unite la 15 m; componenta tare conexă cea mai mare (1141 noduri, 2865 muchii); viteze și timpi de parcurs OSMnx; `population` pe noduri (vezi mai jos) |
| `p3_retea/scenarii_defect.json` | derivat din graf + râul Bega (`waterway=canal`, OSM) | 2026-10-14 | ODbL (date derivate) | `coridor_inundatie`: muchiile la ≤ 40 / 80 / 120 m de albie, la est de Piața Victoriei, în 3 faze (112 muchii); `traversari_rau`: muchiile care traversează Bega (sau poduri OSM la ≤ 60 m de albie) la ≤ 1000 m de centru (7 muchii); `coridor_central`: muchiile la ≤ 150 m de axa P-ța Unirii – P-ța Victoriei – Catedrală (31 muchii) |
| `p3_retea/prioritare.csv` | derivat: `amenity=hospital` (OSM), amprentă ≥ 3000 m²; gara Timișoara Nord | 2026-10-14 | ODbL (date derivate) | 6 spitale; 5 origini pe spital, eșantionate după populație (seed 7), plus gară → fiecare spital: 36 de perechi |
| `p3_retea/importanta_muchii.csv` | calculat: `nx.edge_betweenness_centrality`, exact, ponderat cu `length` | 2026-10-14 | – | – |
| `p3_retea/context.geojson` | OSM: albia Begăi, spitalele, gara | 2026-10-14 | ODbL | doar pentru hărți și vizualizare |
| `ca/Langtons-Loops.rule`, `ca/Langtons-Loops.rle` | Golly (`Rules/`, `Patterns/Loops/`), oglinda GitHub `AlephAlpha/golly` | 2026-10-14 | GPL-2.0 (Golly); citați Langton (1984) | niciuna |

Note:
- **Populația pe noduri e un model, nu o măsurătoare**: suprafața desfășurată a clădirilor rezidențiale OSM (amprentă × `building:levels`; implicit 4 etaje la blocuri, 1 la case), împărțită la 30 m² pe locuitor și atribuită nodului celui mai apropiat. Total ~218 000 de locuitori în zonă. Contează doar ca ponderi la eșantionarea perechilor OD.
- Scenariile în grup sunt **ipotetice**, construite geometric; nu reproduc un eveniment real.
- Toate se refac cu `python scripts/build_dataset.py` (parametrii în `config_de_adaugat.yaml`, secțiunile `osm` și `dataset`).
