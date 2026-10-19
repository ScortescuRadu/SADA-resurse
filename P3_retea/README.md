# P3. Toleranță la defectare pe o rețea de mobilitate: resurse

## Pe scurt

Primiți ce ar fi trebuit să fie în pachetul `p3_retea/`, construit pe centrul Timișoarei:
- rețeaua rutieră, cu populația pe noduri;
- cele trei scenarii de defect în grup;
- perechile prioritare spre spitale;
- importanța muchiilor.

Primiți și regulile buclelor Langton și Byl din Golly, cu o verificare care înlocuiește comparația „cu ochiul” cu Golly.

## Instalare

Din folderul de resurse, cu mediul din kit activat:

```bash
python instaleaza.py P3 ../repo_nostru
```

Ce apare în repo:

| Fișier | La ce folosește |
|---|---|
| `data/p3_retea/retea.graphml` | rețeaua: 1141 de noduri, 2865 de muchii orientate, tare conexă, cu `population` pe noduri |
| `data/p3_retea/scenarii_defect.json` | `coridor_inundatie` (3 faze), `traversari_rau`, `coridor_central` |
| `data/p3_retea/prioritare.csv` | 36 de perechi prioritare: cartiere și gară → 6 spitale |
| `data/p3_retea/importanta_muchii.csv` | edge betweenness exact, ponderat cu lungimea (`u, v, key, importance`) |
| `data/p3_retea/context.geojson` | râul Bega, spitalele, gara, pentru hărți |
| `data/ca/Langtons-Loops.rule/.rle`, `Byl-Loop.rule/.rle` | regulile și configurațiile inițiale, din Golly |
| `src/sada/p3/verificare_golly.py` | verificarea regulilor față de Golly și numărarea buclelor |
| `scripts/build_dataset.py` | reface `data/p3_retea/` din OpenStreetMap (opțional) |

În `config/default.yaml` se schimbă:
- `data.graph`, `data.group_scenarios` (deja corecte în kit), plus cheia nouă `data.importance`;
- `od.priority_file`: din `null` devine `data/p3_retea/prioritare.csv`;
- `osm.dist_m`: 2500 (la 1500 m, cât era în kit, ieșeau doar 463 de noduri, sub minimul de 500 din fișă);
- secțiunea nouă `dataset`, cu parametrii pentru `build_dataset.py`.

## Primii pași

**1. Verificați instalarea:**

```bash
python ../SADA_resurse_studenti/verifica.py P3 .
```

Trebuie să vedeți `1141 noduri, 2865 muchii, 1 componentă tare conexă` și că ambele reguli sunt identice cu arborele Golly.

**2. Pașii 1 și 2 din GHID, pe datele noi:**

```bash
python scripts/inspect_graph.py data/p3_retea/retea.graphml     # desenul ajunge în results/figures/network.pdf
python scripts/prepare_od.py                                     # 300 de perechi + 36 prioritare -> data/od_pairs.csv
```

`prepare_od.py` trebuie să spună `Perechi fără drum în graful intact: 0`.

**3. Uitați-vă la scenarii:**

```python
import json
s = json.load(open("data/p3_retea/scenarii_defect.json"))
print(s["coridor_inundatie"]["descriere"], [len(f) for f in s["coridor_inundatie"]["faze"]])
print(s["traversari_rau"]["descriere"], len(s["traversari_rau"]["muchii"]))
```

## Formatul scenariilor

Fiecare scenariu are o `descriere` și:

- fie `muchii`: listă de `[u, v, cheie]`, cu nodurile și cheia din `retea.graphml`;
- fie `faze`: listă de liste de muchii, aplicate pe rând. Inundația are trei faze, cu apa care crește: muchiile la cel mult 40, 80, apoi 120 m de albie.

Toate scenariile închid ambele sensuri ale unei străzi. Cheile care încep cu `_` (`_format`, `_sursa`) sunt informative, nu scenarii.

`group_failure(G, scenario)` din kit primește un astfel de dicționar. Trebuie să tratați și cazul cu `faze`: fie le aplicați toate odată, fie, mai interesant, câte una pe pas, ca să aveți ce măsura la timpul de recuperare.

## Bucla Langton

```python
from sada.p3.ca import RuleTable, TableCA, read_rle
from sada.p3.verificare_golly import verify_against_tree, CopyTracker

print(verify_against_tree("data/ca/Langtons-Loops.rule"))   # {'neighbourhoods': 32768, 'differences': 0, 'identical': True}

ca = TableCA(RuleTable.from_file("data/ca/Langtons-Loops.rule"))
pat = read_rle("data/ca/Langtons-Loops.rle")
grid = ca.place(pat, shape=(200, 200))
bucle = CopyTracker(pat)
bucle.update(grid)
for t in range(1, 320):
    grid = ca.step(grid)
    inainte = bucle.count
    bucle.update(grid)              # la FIECARE pas
    if bucle.count > inainte:
        print("buclă nouă la pasul", t)   # 151, apoi ~298, ~302 ...
```

**De ce la fiecare pas.** O buclă e în configurația exactă de start un singur pas din ciclul ei, iar buclele unei colonii sunt defazate între ele. `count_structures` din kit numără componentele conexe, care se lipesc și se despart în timpul replicării, deci e zgomotoasă. `CopyTracker` ține minte buclele distincte văzute de la început; e mai sigur pentru perioada de replicare.

**De ce verify_against_tree în loc de Golly.** Fișierele `.rule` conțin și o secțiune `@TREE`, arborele de decizie cu care simulează Golly. Dacă tabelul citit de kit din `@TABLE` dă aceeași stare nouă ca arborele, pe toate cele 8⁵ vecinătăți, fiecare pas al vostru e identic cu pasul din Golly. Spuneți asta în raport ca validare.

## Ce aveți de făcut

Tot ce e marcat TODO în kit:

- [ ] `backup_route` și `precompute` în `routes.py`;
- [ ] `random_failures`, `targeted_failures`, `group_failure` în `failures.py`;
- [ ] `HierarchicalRecovery` (cele trei niveluri ca buclă MAPE-K) în `recovery.py`;
- [ ] `run_one` și experimentele;
- [ ] bucla Langton (și Byl): cel puțin trei replicări, perturbările, comparația cu refacerea rutelor;
- [ ] vizualizarea: `vizualizare/sablon/index.html` redă străzile închise și vehiculele redirecționate din `sim.js`. `vizualizare/exemplu_sim.py` face asta pe inundația de pe Bega și e un punct de plecare bun. Detalii în `vizualizare/README.md`, secțiunea P3.

## La ce să vă așteptați

- **Multe perechi n-o să aibă rută de rezervă complet disjunctă.** Centrul are multe străzi cu sens unic; un nod cu o singură muchie de ieșire face imposibile două drumuri fără muchii comune. Nu e un bug. E una dintre cele mai bune observații pentru raport (GHID: „ce perechi nu au rută de rezervă și de ce?”): numărați câte sunt și din ce cauză.
- **Decideți dacă rezerva are voie pe sensul opus al aceleiași străzi.** Scenariile de aici închid ambele sensuri.
- **Scenariile în grup sunt deterministe.** Vedeți `comun/README.md`.
- **`importanta_muchii.csv` e calculat exact,** nu cu eșantionarea k din config. Dacă recalculați importanța în timpul unui atac adaptiv, acolo aveți nevoie de k.

## Întrebări frecvente

**Pot reface datele?** Da: `python scripts/build_dataset.py`. Are nevoie de OSMnx (în kit) și de internet, și durează câteva minute. Parametrii sunt în secțiunea `dataset`. Rezultatul poate diferi puțin dacă OpenStreetMap s-a schimbat între timp.

**De unde e populația pe noduri?** Din clădirile rezidențiale OSM: suprafața desfășurată împărțită la 30 m² pe locuitor, atribuită nodului celui mai apropiat. E o estimare; vedeți `DATA.md`.

**Spitalele par puține.** `amenity=hospital` din OSM include și cabinete mici; au rămas doar clădirile de peste 3000 m². Toate cele 9 sunt în `context.geojson`; perechile prioritare folosesc primele 6.
