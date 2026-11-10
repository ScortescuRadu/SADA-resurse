# Ghid de implementare: P4, controller pentru frecvența transportului public

Ghidul urmează pașii din fișa proiectului și îi leagă de fișierele din kit. Ordinea e recomandată; dacă aveți o idee mai bună, discutați-o la laborator.

Etapele cu predare (săptămânile 3, 5, 9, 12, 14) au fiecare un fișier în [`milestones/`](milestones/README.md), cu ce trebuie să aveți, codul care vă ajută și ce citiți atunci. Termenii din articole sunt traduși în [`docs/GLOSAR.md`](docs/GLOSAR.md).

## Calendar orientativ

| Săptămâna | Ce ar trebui să aveți |
|---|---|
| 1–2 | mediul instalat, feed-ul descărcat și inspectat, exemplul de jucărie rulat; pasul 1 |
| 3 | pașii 2–3: S0 și încărcările; liniile alese; tema confirmată |
| 4–5 | pasul 4 (regula simplă) pe o fereastră; nota de proiectare |
| 6–8 | pașii 5–6: algoritmul genetic și acoperirea |
| 9 | **prototip**: controllerul rulează pe 07:00–09:00 și mută cel puțin o cursă, vizibil în jurnal |
| 10–11 | pașii 7–8: perturbările și experimentele complete |
| 12 | varianta de lucru a raportului |
| 13–14 | figuri finale, prezentare, verificarea reproductibilității |

## Noțiuni de care aveți nevoie

- **Intervalul de succedare** (headway): timpul dintre două vehicule consecutive ale aceleiași linii, în aceeași stație. Frecvența este inversul lui.
- **Timpul mediu de așteptare**: dacă pasagerii sosesc la întâmplare, aproximativ jumătate din interval.
- **Capacitatea oferită** într-o fereastră: numărul de curse × capacitatea unui vehicul.
- **Gradul de încărcare**: pasagerii împărțiți la capacitatea oferită. Peste 85%: supraaglomerat; sub 30%: subutilizat (pragurile din fișă).
- **Ore-vehicul**: cât timp sunt vehiculele în serviciu, inclusiv timpul de întoarcere la capăt. E „bugetul” controllerului: totalul rămâne constant.

---

## Pasul 1. Citiți feed-ul

**Unde:** `src/sada/p4/gtfs_io.py` (gata), `scripts/download_gtfs.py`, `scripts/inspect_gtfs.py`.

```bash
python scripts/download_gtfs.py
python scripts/inspect_gtfs.py --date 2026-10-14
```

Alegeți o zi lucrătoare din perioada de valabilitate (scrieți-o în `gtfs.date`). `active_service_ids` ține cont și de excepții (sărbători), deci verificați că ziua aleasă are servicii active. Alegeți 10–15 linii care acoperă tramvai, troleibuz și autobuz și trec printr-o zonă periferică cu acces slab (lista zonelor e în pachet); treceți-le în `gtfs.routes`.

## Pasul 2. Orarul de referință S0

**Unde:** `src/sada/p4/baseline.py` (gata), `scripts/baseline_s0.py`.

```bash
python scripts/baseline_s0.py
```

Pentru fiecare linie, în fereastra 07:00–09:00: numărul de curse care pleacă din capăt, intervalul mediu și orele-vehicul (suma duratelor + un timp de întoarcere la capăt pe cursă, `gtfs.layover_min`). Totalul de ore-vehicul e bugetul controllerului.

Layover-ul de 5 minute e o ipoteză. Dacă feed-ul are `block_id` în `trips.txt`, puteți calcula timpul real dintre curse consecutive ale aceluiași vehicul; altfel spuneți în raport ce ați presupus.

## Pasul 3. Încărcările

**Unde:** cod nou, de exemplu `src/sada/p4/load.py`.

Tabelul din pachet dă pasagerii pe linie și pe fereastră de 15 minute. Pentru fiecare linie și fereastră:

```
capacitate_oferită = curse_în_fereastră × capacitate_vehicul(mod)
grad_de_încărcare  = pasageri / capacitate_oferită
```

Verificați că în S0 există linii peste 85% și sub 30%. Dacă nu există, controllerul n-are ce realoca; discutați la laborator.

**Ipoteza despre cerere.** Cea mai simplă: numărul de pasageri pe linie nu se schimbă când se schimbă frecvența (cerere inelastică). E rezonabilă pe termen scurt și trebuie spusă în raport. O variantă mai realistă, opțională: o parte din pasageri trec pe o linie paralelă dacă intervalul crește mult.

## Pasul 4. Regula simplă

**Unde:** `src/sada/p4/controller.py`, `SimpleRuleController`. Pentru structură, uitați-vă întâi la `examples/toy_mapek.py` și la `docs/MAPEK.md`.

| Etapă | Ce face concret |
|---|---|
| M | la fiecare 15 minute: încărcarea fiecărei linii în ultima fereastră |
| A | liniile peste 85% și sub 30% |
| P | mută o cursă (sau orele-vehicul echivalente) de pe linia cea mai puțin încărcată pe cea mai încărcată |
| E | actualizează numărul de curse pe linie pentru fereastra următoare |
| K | orarul S0, alocările anterioare, jurnalul |

Restricții: totalul de ore-vehicul rămâne cel din S0; nicio linie nu depășește intervalul maxim (`max_headway_min`), ca să nu rămână practic fără serviciu. O cursă pe o linie lungă costă mai multe ore-vehicul decât pe una scurtă; când mutați, convertiți prin orele-vehicul pe cursă.

## Pasul 5. Alocarea prin algoritm genetic

**Unde:** `src/sada/p4/ga_alloc.py` și `GAController.plan`.

- **Individ:** vector întreg cu numărul de curse pe fiecare linie în fereastra următoare.
- **Limite:** minimul care respectă intervalul maxim; maximul pe care îl permite flota.
- **Constrângere:** Σ curse_i × ore_vehicul_pe_cursă_i ≤ bugetul S0. Reparare: scădeți curse de pe liniile cu cel mai mic câștig până intrați în buget.
- **Fitness:** de exemplu −(1000 × pasageri în curse peste 100% + timpul mediu de așteptare ponderat cu pasagerii). Spuneți ce ponderi ați ales și de ce.
- **Operatori:** turnir; încrucișare uniformă pe linii; mutație care mută o cursă de pe o linie pe alta (păstrează aproximativ bugetul).

Un algoritm genetic rulat la fiecare fereastră de 15 minute trebuie să fie rapid: populație de 40–60, 50–100 de generații, pornind de la alocarea curentă (plus câteva variații) ca să nu o ia de la zero.

Comparați algoritmul genetic și regula simplă **la același buget de ore-vehicul**.

## Pasul 6. Acoperirea

**Unde:** `src/sada/p4/coverage.py`; proiecția e gata în `gtfs_io.stops_xy`.

Metrica din fișă: ponderea populației aflate la cel mult 400 m de o stație cu interval de cel mult 20 de minute.

1. Stațiile bine deservite: cele prin care trece cel puțin o linie cu interval ≤ 20 min în fereastra curentă.
2. Coordonatele, în metri: `stops_xy(feed)` folosește Stereo 70 (EPSG:3844), sistemul național.
3. Populația: centroizii zonelor din `common/` (sau punctele de populație din pachet), proiectați la fel.
4. `scipy.spatial.cKDTree(stații).query_ball_point(puncte, r=400)` și însumați populația punctelor care au cel puțin o stație în rază.

Distanța în linie dreaptă subestimează distanța reală de mers; spuneți asta în secțiunea de limite.

## Pasul 7. Perturbările

**Unde:** `run_one` din `experiments.py`, după `scenarios` din config.

- **Scoaterea unei linii din circulație:** decideți dacă orele-vehicul ale ei devin disponibile pentru celelalte linii (vehiculele sunt mutate) sau se pierd (vehiculele sunt blocate). Ambele sunt plauzibile; alegeți și justificați. Pasagerii liniei închise trebuie să meargă undeva: cea mai simplă ipoteză e că se mută pe liniile care au stații comune.
- **Creșterea cererii cu 20% într-o zonă:** înmulțiți încărcările liniilor care trec prin zonă (o linie „trece” dacă are cel puțin o stație în zonă).

Controllerul nu știe dinainte când apar; le vede doar prin încărcări.

## Pasul 8. Experimentele

**Metrici** (pe fereastra 07:00–09:00):

- `overcrowded_trip_pct`: ponderea curselor cu încărcare peste 100%;
- `mean_wait_min`: timpul mediu de așteptare (jumătate din interval), ponderat cu pasagerii;
- `vehicle_hours`: orele-vehicul consumate (trebuie să rămână cel mult cât S0);
- `coverage_pct`: ponderea populației acoperite.

**Experimentele minime din fișă:**

- orarul real ca referință (S0) pe 07:00–09:00;
- controllerul cu algoritm genetic comparat cu regula simplă, la același buget;
- două perturbări: scoaterea unei linii și creșterea cererii cu 20% într-o zonă.

Variabilitatea între rulări vine din algoritmul genetic și, dacă o modelați, din cerere (de exemplu pasageri Poisson în jurul încărcării din tabel). Fără nicio componentă aleatoare, S0 și regula simplă dau același rezultat la fiecare rulare; spuneți asta.

**Figuri recomandate:** intervalele pe linie în S0 vs. după controller (bare grupate); încărcarea pe linie și fereastră ca hartă termică (linii × ferestre), înainte și după; o hartă cu stațiile și zonele acoperite. Pentru demonstrație: încărcarea liniei afectate de perturbare în timp, cu deciziile controllerului marcate.

---

## Greșeli frecvente

- **Ore după miezul nopții** (25:10:00) convertite cu datetime. `time_to_seconds` le tratează corect.
- **Zile amestecate.** Fără filtrarea serviciilor pe o singură zi, numărul de curse iese de câteva ori prea mare.
- **Timpul de întoarcere uitat.** Orele-vehicul sunt subestimate și controllerul pare să aibă mai multă flotă decât are.
- **Linie lăsată fără serviciu.** Fără intervalul maxim, controllerul poate muta toate cursele de pe o linie periferică, exact cea pe care fișa o vrea deservită.
- **Încărcări prezentate ca reale.** Sunt din model.

## Întrebări de verificare înainte de prezentare

- Cum ați calculat orele-vehicul și ce ați presupus despre timpul de întoarcere?
- Ce se întâmplă cu pasagerii când mutați o cursă de pe o linie?
- De ce ar face algoritmul genetic mai bine decât regula simplă? Când nu face?
- Ce înseamnă acoperirea de 400 m și ce aproximare ați folosit?
- Ce s-ar schimba dacă ați avea validări reale în loc de un model de cerere?
