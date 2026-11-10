# Ghid de implementare: P3, toleranță ierarhică la defectare

Ghidul urmează pașii din fișa proiectului și îi leagă de fișierele din kit. Ordinea e recomandată; dacă aveți o idee mai bună, discutați-o la laborator.

Etapele cu predare (săptămânile 3, 5, 9, 12, 14) au fiecare un fișier în [`milestones/`](milestones/README.md), cu ce trebuie să aveți, codul care vă ajută și ce citiți atunci. Termenii din articole sunt traduși în [`docs/GLOSAR.md`](docs/GLOSAR.md).

## Calendar orientativ

| Săptămâna | Ce ar trebui să aveți |
|---|---|
| 1–2 | mediul instalat, graful încărcat și desenat, exemplul de jucărie rulat; pașii 1–2 |
| 3 | pașii 3–4 (rute de rezervă, importanța muchiilor); tema confirmată |
| 4–5 | pasul 5 (defectele) și primul experiment fără recuperare; nota de proiectare |
| 6–8 | pasul 6 (cele trei nivele); pasul 7 pornit (bucla Langton) |
| 9 | **prototip**: o defecțiune în grup, sistemul o detectează și comută pe rute de rezervă, vizibil în jurnal |
| 10–11 | pașii 7–8 terminați: bucla cu cel puțin trei replicări, experimentele complete |
| 12 | varianta de lucru a raportului, inclusiv secțiunea despre autoreplicare |
| 13–14 | figuri finale, prezentare, verificarea reproductibilității |

## Ideea, pe scurt

Codurile corectoare de erori ierarhice tratează o eroare mică local, iar una mai mare la un nivel superior. Aplicat unei rețele rutiere:

| Nivel | Analog cu codurile | În rețea |
|---|---|---|
| 1, detecție | sindromul arată că există o eroare | perechile OD ale căror rute conțin muchii căzute |
| 2, corecție | eroarea se corectează local, cu redundanța existentă | comutare pe ruta de rezervă calculată dinainte |
| 3, degradare controlată | eroarea e prea mare; se salvează ce se poate | se servesc doar perechile prioritare cu ce a rămas |

---

## Pasul 1. Graful

**Unde:** `src/sada/p3/graph_io.py` (gata), `scripts/inspect_graph.py`.

```bash
python scripts/inspect_graph.py data/p3_retea/<graf>.graphml
```

Verificați: numărul de noduri și muchii; dacă graful e orientat (rețelele rutiere au de obicei străzi cu sens unic, deci da); dacă e tare conex; ce atribut are lungimea (`length`) și dacă nodurile au `population`. Desenul ajunge în `results/figures/network.pdf`.

## Pasul 2. Perechile OD

**Unde:** `src/sada/p3/od.py` (gata), `scripts/prepare_od.py`.

```bash
python scripts/prepare_od.py --n 300
```

300 de perechi eșantionate proporțional cu populația, plus perechile prioritare (dacă dați un fișier CSV cu ele). Lista se salvează în `data/od_pairs.csv`, împreună cu costul de bază, și se refolosește în toate experimentele. Nu o regenerați între experimente.

## Pasul 3. Rutele principale și de rezervă

**Unde:** `src/sada/p3/routes.py`: `backup_route` și `precompute`.

Pentru fiecare pereche: ruta principală (`primary_route`, gata) și o rută de rezervă fără muchii comune. Varianta cea mai simplă:

```python
edges = path_edges(G, primary)                              # (u, v, cheie)
H = nx.restricted_view(G, nodes=[], edges=edges)            # vedere fără copiere
try:
    return nx.shortest_path(H, o, d, weight=weight)
except nx.NetworkXNoPath:
    return None
```

Atenție la străzile cu dublu sens: muchia u→v și muchia v→u sunt diferite într-un graf orientat. Decideți dacă ruta de rezervă are voie să folosească sensul opus al aceleiași străzi (o inundație le blochează pe amândouă) și spuneți ce ați ales.

`precompute` construiește dicționarul cu ambele rute și mulțimile lor de muchii, pentru verificări rapide. Aceasta e partea K a buclei.

**Cum verificați:** `test_backup_route_is_edge_disjoint`. Câte perechi nu au rută de rezervă? E o informație bună pentru raport (puncte vulnerabile ale rețelei).

## Pasul 4. Importanța muchiilor

**Unde:** `edge_importance` din `failures.py` (gata), `scripts/compute_importance.py`.

Lista din pachet e un punct de pornire. Recalcularea cu `nx.edge_betweenness_centrality` pe un graf de câteva mii de noduri durează mult; parametrul `k` eșantionează k noduri sursă și face calculul aproximativ, mult mai rapid. Spuneți în raport ce k ați folosit.

## Pasul 5. Defectele

**Unde:** `src/sada/p3/failures.py`.

- `random_failures(G, frac, rng)`: muchii alese uniform.
- `targeted_failures(G, frac, importance, recompute)`: cele mai importante muchii, în ordine. Cu `recompute=True`, importanța se recalculează după fiecare eliminare (atac adaptiv; mai realist și mult mai lent). Alegeți și spuneți.
- `group_failure(G, scenario)`: muchiile unui scenariu din fișierul de sinteză.

Pentru eliminarea progresivă (până la 10%), împărțiți lista în `failures.steps` trepte și măsurați după fiecare treaptă.

**Primul rezultat, fără recuperare:** procentul de perechi OD conectate în funcție de fracțiunea de muchii eliminate, aleator vs. țintit. Așa arată figura clasică din Albert, Jeong și Barabási (2000): rețeaua rezistă bine la defecte aleatoare și cedează repede la atacuri țintite.

## Pasul 6. Cele trei nivele (MAPE-K)

**Unde:** `src/sada/p3/recovery.py`. Pentru structură, uitați-vă întâi la `examples/toy_mapek.py` și la `docs/MAPEK.md`.

| Etapă | Ce face concret |
|---|---|
| M | muchiile căzute de la ultimul ciclu; numărul de componente conexe |
| A | perechile afectate (rute care conțin muchii căzute); procentul deconectat; tipul defectului |
| P | pentru fiecare pereche afectată: nivelul 2 dacă rezerva e intactă, altfel nivelul 3 |
| E | actualizează ruta curentă a perechii; marchează perechile în serviciu degradat |
| K | rutele din `precompute`, mulțimile de muchii, jurnalul cu nivelul care a rezolvat fiecare caz |

**Nivelul 1** nu recalculează nimic pentru tot graful: verifică doar intersecția dintre muchiile căzute și muchiile rutelor curente. Așa rămâne rapid chiar și pe 3000 de noduri.

**Nivelul 3** recalculează drumuri pe graful avariat doar pentru perechile prioritare. Dacă vreți să modelați „capacitatea rămasă”, cea mai simplă variantă e o limită pe numărul de perechi care pot fi rerutate pe aceeași muchie; spuneți ce ați presupus.

**Timpul de recuperare.** Definiți un pas de simulare (de exemplu, un ciclu al buclei) și numărați pașii până când toate perechile care pot fi recuperate sunt recuperate. Scrieți definiția în raport.

**Cum verificați:** pe un scenariu de defect în grup, jurnalul trebuie să arate câte perechi a rezolvat fiecare nivel. O hartă cu muchiile căzute (roșu) și câteva rute de rezervă (verde) e o figură foarte bună pentru prezentare.

## Pasul 7. Bucla Langton

**Unde:** `src/sada/p3/ca.py` (motorul și citirea fișierelor sunt gata), `scripts/run_ca.py`.

Bucla Langton are 8 stări, vecinătate von Neumann (nord, est, sud, vest) și un tabel de reguli aplicat pentru toate cele patru rotații ale vecinătății. Bucla ocupă aproximativ 10 × 15 celule. „Genomul” ei e o secvență de perechi (stare nenulă, 0) care circulă în jurul buclei și iese printr-un braț; brațul construiește bucla-fiică, care se desprinde după aproximativ 151 de pași. O buclă nu se poate replica într-un spațiu deja ocupat, așa că o colonie crește la margine și rămâne „moartă” în interior. Bucla Byl (1989) e mult mai mică (12 celule) și se replică în aproximativ 25 de pași, deci e mai ușor de urmărit. Regula și configurația inițială le luați din Golly (vedeți `DATE.md`).

```bash
python scripts/run_ca.py --rule data/ca/Langtons-Loops.rule --pattern data/ca/<model>.rle --size 128 --steps 1200
```

Ce aveți de făcut:

1. Verificați că evoluția coincide cu cea din Golly la câțiva pași aleși. Un al doilea test simplu: perioada de replicare măsurată de voi (pasul la care numărul de structuri crește de la 1 la 2) trebuie să fie apropiată de valoarea din literatură.
2. Arătați cel puțin trei replicări (instantanee și numărul de structuri în timp, cu `count_structures`).
3. **Perturbați mediul:** modificați o celulă dintr-o buclă (sau din „brațul” ei) la un moment dat și urmăriți ce se întâmplă. Repetați pentru câteva poziții și momente.

Secțiunea din raport (1–2 pagini) compară autoreplicarea cu refacerea unei rute:

| Întrebare | Bucla Langton | Rețeaua |
|---|---|---|
| ce se copiază? | instrucțiunile care circulă în buclă | structura rutei (precalculată) |
| ce condiții sunt necesare? | spațiu liber pe grilă | muchii disponibile, rută de rezervă intactă |
| ce se pierde la o perturbare? | ce ați observat la punctul 3 | ce se pierde când pică și ruta de rezervă |

## Pasul 8. Experimentele

**Unde:** `src/sada/p3/experiments.py` (`run_one`), apoi `scripts/run_all.py`.

**Metrici** (vedeți `metrics.py`, gata): procentul de perechi OD conectate, creșterea costului mediu de parcurs (doar pe perechile conectate), numărul de rute de rezervă folosite, timpul de recuperare în pași.

**Experimentele minime din fișă:**

- eliminarea progresivă a muchiilor, aleatoare și țintită, până la 10% din rețea;
- cele trei scenarii de defect în grup, cu și fără recuperare pe nivele;
- comparația: fără recuperare, doar nivelul 2, nivelurile 1–3 împreună.

La scenariile în grup nu există nimic aleator; repetați doar dacă metoda voastră are o componentă aleatoare. Defectele aleatoare se repetă cu seed-uri diferite (cel puțin 20).

---

## Greșeli frecvente

- **Recalcularea tuturor rutelor după fiecare muchie eliminată.** Durează foarte mult; recalculați doar perechile afectate.
- **Graf orientat tratat ca neorientat**, sau invers. Verificați la încărcare.
- **Noduri citite ca text într-un loc și ca numere în altul** (CSV vs. GraphML). `metrics._match` tratează cazurile uzuale; folosiți aceeași convenție peste tot.
- **„Pas de simulare” nedefinit.** Timpul de recuperare n-are sens fără definiție.
- **Grilă prea mică pentru buclă.** Replicile se lovesc de margine sau între ele.

## Întrebări de verificare înainte de prezentare

- De ce rezistă rețeaua mai bine la defecte aleatoare decât la atacuri țintite?
- Ce perechi n-au rută de rezervă și de ce?
- De ce e nivelul 1 rapid?
- Ce presupuneți despre capacitate la nivelul 3?
- Ce se copiază într-o buclă Langton și ce o distruge?
