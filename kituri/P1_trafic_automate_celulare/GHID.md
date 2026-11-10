# Ghid de implementare: P1, trafic cu automate celulare

Ghidul urmează pașii din fișa proiectului și îi leagă de fișierele din kit. La fiecare pas găsiți ce faceți, unde, cum verificați că merge și ce greșeli apar des. Ordinea e recomandată; dacă aveți o idee mai bună, discutați-o la laborator.

Etapele cu predare (săptămânile 3, 5, 9, 12, 14) au fiecare un fișier în [`milestones/`](milestones/README.md), cu ce trebuie să aveți, codul care vă ajută și ce citiți atunci. Termenii din articole sunt traduși în [`docs/GLOSAR.md`](docs/GLOSAR.md).

## Calendar orientativ

| Săptămâna | Ce ar trebui să aveți |
|---|---|
| 1–2 | mediul instalat, datele deschise, exemplul de jucărie rulat; pașii 1–2 |
| 3 | pasul 3 (diagrama fundamentală); tema confirmată |
| 4–5 | pasul 4; nota de proiectare (2 pagini, cu diagrama MAPE-K schițată) |
| 6–8 | pașii 5–6: coridorul și controllerul |
| 9 | **prototip**: coridorul rulează și controllerul ia cel puțin o decizie vizibilă în jurnal |
| 10–11 | pașii 7–8: referința SUMO, perturbările, rulările complete |
| 12 | varianta de lucru a raportului |
| 13–14 | figuri finale, prezentare, verificarea reproductibilității |

## Modelul, pe scurt

Drumul e împărțit în celule de 7,5 m. Fiecare celulă e goală sau are un vehicul cu viteza v ∈ {0, …, vmax}, în celule pe pas. La fiecare pas (1 s), toate vehiculele aplică simultan:

1. **accelerare:** v ← min(v + 1, vmax)
2. **frânare:** v ← min(v, gap), unde gap = celulele libere până la vehiculul din față
3. **încetinire aleatoare:** cu probabilitatea p, v ← max(v − 1, 0)
4. **deplasare:** poziția crește cu v

Cu vmax = 2 celule/pas, viteza maximă e 15 m/s ≈ 54 km/h, potrivită pentru o stradă cu limita de 50 km/h.

Variantele modifică pornirea din coloană:

- **VDR** (velocity-dependent randomization): vehiculele oprite folosesc o probabilitate de încetinire mai mare, p0 > p.
- **Slow-to-start**: un vehicul care a fost blocat mai stă un pas după ce i se eliberează drumul.

Ambele fac ca ambuteiajele să se dizolve mai greu, ceea ce seamănă mai mult cu traficul urban real.

---

## Pasul 1. NaSch pe un inel

**Unde:** `src/sada/p1/nasch.py`, metoda `RingRoad.step`.

O singură bandă, condiții periodice (inel). Pozițiile și vitezele sunt vectori NumPy; `gaps()` e deja scris.

Ideea de implementare, vectorizat:

```python
gaps = self.gaps()
v = np.minimum(self.vel + 1, self.vmax)          # 1
v = np.minimum(v, gaps)                          # 2
slow = self.rng.random(self.n) < self.p          # 3
v = np.where(slow, np.maximum(v - 1, 0), v)
pos = (self.pos + v) % self.L                    # 4
# reordonare: pos și v împreună
```

**Cum verificați:** `pytest -q tests/test_p1_nasch.py`. Testele verifică numărul constant de vehicule, lipsa coliziunilor, atingerea vitezei maxime la densitate mică și apariția ambuteiajelor la densitate mare.

**Greșeala tipică:** actualizare secvențială (un vehicul se mută, apoi următorul își calculează distanța față de noua poziție). NaSch e paralel: toate vitezele noi se calculează din starea veche.

## Pasul 2. Diagrama spațiu-timp

**Unde:** `scripts/space_time.py` (gata).

```bash
python scripts/space_time.py --density 0.3 --p 0.3
```

Pe orizontală pozițiile, pe verticală timpul, culoarea e viteza. Vehiculele oprite (culoare închisă) formează dungi care coboară spre stânga: ambuteiajul se deplasează înapoi, contra sensului de mers, cu aproximativ o celulă pe pas. Dacă nu vedeți asta la densitate 0,3–0,4, regulile au o greșeală. Figura asta e bună și pentru raport și prezentare: arată dintr-o privire ce face modelul.

## Pasul 3. Diagrama fundamentală

**Unde:** `src/sada/p1/fundamental.py` și `scripts/fundamental_diagram.py` (gata).

```bash
python scripts/fundamental_diagram.py
```

Pentru fiecare densitate se rulează o perioadă de încălzire, apoi se măsoară fluxul (densitate × viteză medie). `to_physical` transformă în veh/km/bandă și veh/h/bandă. Curba urcă, atinge un maxim la **densitatea critică**, apoi coboară.

Notați densitatea critică și fluxul maxim: de aici veți alege pragurile controllerului (pasul 6) și debitele scenariilor (pasul 8).

## Pasul 4. VDR și slow-to-start

**Unde:** tot `RingRoad.step`, după valoarea `self.rule`.

- **VDR:** la pasul 3, vehiculele care aveau v = 0 la începutul pasului folosesc `self.p0` în loc de `self.p`: `pr = np.where(v_vechi == 0, self.p0, self.p)`.
- **Slow-to-start:** după accelerare, vehiculele cu `self.blocked_before` adevărat și gap > 0 rămân la 0. La finalul pasului, `blocked_before = (v == 0) & (gaps == 0)`, reordonat împreună cu pozițiile.

**Cum verificați:** testul `test_variants_lower_flow_than_nasch_in_congestion` și diagrama fundamentală: ambele variante dau un flux maxim mai mic. VDR arată, în plus, histerezis: pentru aceeași densitate, fluxul depinde de starea de pornire (porniți o dată cu vehiculele distribuite uniform, o dată cu toate grămadă, și comparați).

## Pasul 5. Coridorul

**Unde:** `src/sada/p1/corridor.py`, clasa `Corridor`.

Diferențe față de inel:

- **2–3 benzi.** O matrice benzi × celule e cea mai simplă reprezentare: `-1` pentru gol, altfel viteza. Separat, un vector cu momentul de intrare al fiecărui vehicul, pentru timpul de parcurs.
- **Intrare deschisă.** La fiecare pas, numărul de vehicule care încearcă să intre e `rng.poisson(inflow_per_step)`, repartizate pe benzi. Un vehicul intră doar dacă prima celulă a benzii e liberă; altfel rămâne la coadă (țineți o coadă de intrare și raportați-o, e o metrică utilă).
- **Ieșire deschisă.** Vehiculele care depășesc ultima celulă dispar; le notați timpul de parcurs.
- **Schimbarea benzii.** Regulă simplă, aplicată înaintea pașilor NaSch: un vehicul trece pe banda vecină dacă gap-ul în față pe banda lui e mai mic decât v + 1, pe banda vecină gap-ul în față e mai mare, iar în spate, pe banda vecină, are cel puțin vmax celule libere. Faceți schimbările tot în paralel.
- **Tronsoane.** `segment_cells` celule pe tronson. Fiecare tronson are regula lui (`segment_rule`), deci la pasul 3 al NaSch probabilitatea de încetinire depinde de tronsonul în care se află vehiculul.

**Cum verificați:** fără controller, cu o singură regulă și o bandă, coridorul la debit mic trebuie să dea timpul de parcurs aproape de lungime / viteza maximă (4000 m / 15 m/s ≈ 267 s, plus încetinirile aleatoare). Desenați o diagramă spațiu-timp pentru o bandă.

## Pasul 6. Controllerul

**Unde:** `src/sada/p1/controller.py`. Pentru structură, uitați-vă întâi la `examples/toy_mapek.py` și la `docs/MAPEK.md`.

| Etapă | Ce face concret |
|---|---|
| M | la fiecare `window_s` secunde: densitatea [veh/km/bandă] și viteza medie [km/h] pe fiecare tronson, mediate pe fereastră |
| A | regimul fiecărui tronson: liber / aglomerat / blocat, cu praguri cu histerezis |
| P | regula (și eventual p sau vmax) pentru fiecare tronson, în funcție de regim |
| E | `corridor.set_rule(segment, rule)` |
| K | regimul anterior pe tronsoane (pentru histerezis), jurnalul schimbărilor |

**Pragurile.** Porniți de la densitatea critică din pasul 3. De exemplu: „aglomerat” peste 0,8 × densitatea critică, „blocat” peste 1,5 × densitatea critică, iar ieșirea din fiecare regim la un prag cu 10–20% mai mic. Valorile acestea sunt doar un punct de pornire; în raport justificați ce ați ales.

**Ce regulă pe ce regim?** E întrebarea de cercetare a proiectului. O ipoteză de lucru: în trafic liber regula contează puțin; în trafic aglomerat, regula care descrie cel mai bine comportamentul real la pornire (VDR sau slow-to-start) dă predicții mai realiste. Alternativ, controllerul poate regla p sau vmax pe tronson (ca un sistem de limitare variabilă a vitezei) ca să întârzie formarea ambuteiajelor. Alegeți și formulați clar ce optimizați.

**Prototipul din săptămâna 9** trebuie să arate cel puțin o linie în jurnal de tipul `t=1800, tronson 4: aglomerat -> vdr`.

## Pasul 7. Referința SUMO

**Unde:** `scripts/build_sumo_net.py`, `scripts/make_flows.py`, `src/sada/p1/sumo_tools.py`.

1. Rețeaua: din pachet sau `python scripts/build_sumo_net.py`.
2. Deschideți-o în `netedit` și notați ID-urile muchiilor de la capetele coridorului; completați `sumo.from_edge` și `sumo.to_edge` în config.
3. Cererea: `python scripts/make_flows.py --profile data/p1_coridor/<profil>.csv`.
4. Detectoarele: câte un detector E1 în dreptul fiecărui tronson al automatului (`write_e1_detectors`). ID-urile benzilor le vedeți tot în netedit (au forma `<muchie>_<indexbandă>`).
5. Rulați cu `run_sumo(...)` și citiți rezultatul cu `read_e1_output(...)`.

Pentru diagrama fundamentală din SUMO, grupați intervalele de 60 s după densitate (ocupanța detectorului e o aproximare a densității) și desenați fluxul. Nu vă așteptați la aceeași curbă: SUMO folosește alt model de urmărire (Krauss implicit) și altă geometrie. Ce comparați e forma și ordinul de mărime; discutați diferențele în raport.

## Pasul 8. Perturbări și experimente

**Unde:** `src/sada/p1/experiments.py` (`run_one`), apoi `scripts/run_all.py` și `scripts/make_figures.py`.

**Incidentul de 120 s:** `corridor.block(lane, cell, True)` la `start_s`, `False` la `start_s + 120`. O celulă blocată se comportă ca un vehicul cu viteza 0.

**Metricile** (doar după încălzire):

- `travel_time_mean` [s]: media timpilor de parcurs ai vehiculelor care au ieșit;
- `throughput` [veh/h]: vehicule ieșite pe oră;
- `recovery_time` [s]: de la sfârșitul incidentului până când viteza medie pe tronsonul afectat revine la 90% din media dinainte de incident și rămâne acolo cel puțin o fereastră. Spuneți în raport pragul folosit. Pentru scenariile fără incident întoarceți `nan`.

**Experimentele minime din fișă:**

- diagrama fundamentală pentru CA și SUMO, pe același coridor;
- trei regimuri de cerere (scăzută, medie, ridicată) cu regulă fixă, comparate cu controllerul adaptiv;
- o perturbare: incidentul de 120 s pe o bandă sau o creștere bruscă a cererii;
- cel puțin 20 de rulări pe scenariu, cu media și abaterea standard.

Scenariile și variantele sunt deja în `config/default.yaml`; ajustați debitele după diagrama fundamentală (cererea „ridicată” trebuie să fie aproape sau peste capacitate).

**Figuri recomandate pentru raport:** diagrama spațiu-timp; diagrama fundamentală CA vs. SUMO; boxplot-urile timpului de parcurs pe scenarii (le face `make_figures.py`); o figură în timp cu viteza pe tronsonul incidentului, pentru varianta fixă și cea adaptivă, cu momentele în care controllerul a schimbat regula marcate pe axă. Ultima arată adaptarea și e cea mai importantă la demonstrație.

---

## Greșeli frecvente

- **Actualizare secvențială în loc de paralelă** (pasul 1).
- **Praguri fără histerezis.** Controllerul schimbă regula la fiecare fereastră când densitatea stă în jurul pragului.
- **Unități amestecate.** Raportați fluxul în veh/h și densitatea în veh/km, la fel pentru CA și SUMO.
- **Metrici calculate din primul minut.** Primele minute reflectă starea inițială; folosiți `warmup_s`.
- **Coada de la intrare ignorată.** Dacă vehiculele nu mai pot intra, timpul de parcurs al celor din coridor poate arăta bine deși sistemul e saturat. Raportați și coada sau timpul de așteptare la intrare.

## Întrebări de verificare înainte de prezentare

- Ce înseamnă un pas de simulare și o celulă, în unități fizice?
- De ce apar ambuteiaje fără niciun obstacol?
- Ce diferă între VDR și slow-to-start și cum se vede în diagrama fundamentală?
- De ce ați ales pragurile acelea?
- Ce s-ar întâmpla fără histerezis?
- În ce condiții controllerul adaptiv nu ajută?
