# P1. Trafic cu automate celulare: resurse

## Pe scurt

Primiți un script care rulează în SUMO același coridor ca automatul vostru: drept, aceeași lungime, aceleași benzi și tronsoane, aceleași scenarii din config. E referința cerută de fișă (GHID.md, pasul 7), gata de folosit, ca să vă puteți concentra pe automat și pe controller.

Nu e nevoie de date noi: P1 nu depinde de pachetul disciplinei pentru coridor.

## Instalare

Din folderul de resurse, cu mediul din kit activat:

```bash
python instaleaza.py P1 ../repo_nostru
```

Ce apare în repo:

| Fișier | La ce folosește |
|---|---|
| `scripts/sumo_coridor_drept.py` | construiește coridorul în SUMO și rulează scenariile |
| `src/sada/statistica_pereche.py` | comparații pereche pe seed (vedeți `comun/README.md`) |
| `data/timisoara/` | baza cu datele despre oraș (opțională pentru voi; vedeți `comun/timisoara/README.md`) |

Config-ul nu se schimbă: scriptul folosește cheile din secțiunea `model` care sunt deja în kit.

## Primii pași

**1. Verificați că SUMO e instalat** (kitul îl instalează prin pip, pachetul `eclipse-sumo`):

```bash
python ../SADA_resurse_studenti/verifica.py P1 .
```

Trebuie să vedeți `[ok]` la `sumo` și `netconvert`.

**2. Rulați referința**, întâi pe un singur seed, ca test (durează sub un minut):

```bash
python scripts/sumo_coridor_drept.py --runs 1
```

Ieșirea arată așa, cu câte o linie pe scenariu:

```
Rețea: data/sumo/coridor_drept.net.xml (10 muchii de 400 m, 2 benzi)
  cerere_scazuta   timp de parcurs  294.8 s, debit    634 veh/h
  ...
```

**3. Rulați pe cât de multe seed-uri vă trebuie** pentru raport (10 e un minim rezonabil; ~10 s pe rulare):

```bash
python scripts/sumo_coridor_drept.py --runs 10
```

## Ce produce

| Fișier | Conținut |
|---|---|
| `data/sumo/coridor_drept.net.xml` | rețeaua SUMO: 10 muchii de 400 m (una pe tronson), `lanes` benzi, viteza maximă = `vmax · cell_m / dt_s` |
| `results/sumo/sumo_results.csv` | o linie pe (scenariu, seed): `travel_time_mean`, `throughput`, `wait_mean`, cu `variant = sumo` |
| `results/sumo/sumo_speed.csv` | viteza medie [km/h] pe tronson, la fiecare 10 s, pe scenariu și seed |
| `results/sumo/fd_sumo.csv` | puncte (densitate, flux, viteză) din detectoare, la 60 s, dintr-o rampă de cerere |

Coloanele din `sumo_results.csv` au aceleași nume ca în `results.csv` al vostru. Le puteți lipi una sub alta (`pd.concat`) și face tabelul „automat vs. SUMO” direct.

## Cum e construit

- **Vehiculele.** Lungimea plus distanța minimă e 7,5 m, exact o celulă. Viteza maximă e `vmax` din config.
- **Cererea.** E un flux Bernoulli pe secundă, adică echivalentul sosirilor Poisson din automat.
- **Incidentul.** E un vehicul oprit pe banda și la poziția din config, pe durata din config.
- **Vârful de cerere.** Dacă adăugați în scenariu `surge: {start_s: 1800, duration_s: 600, inflow_veh_h: 2800}`, scriptul îl înțelege.
- **Detectoarele.** Câte unul pe fiecare bandă, la mijlocul fiecărui tronson.
- **Diagrama fundamentală.** Se face dintr-o cerere care crește până peste capacitate, plus un incident, ca să apară și ramura congestionată.

De ce un coridor drept și nu rețeaua din OSM pe care o construiește kitul (`build_sumo_net.py`): pe rețeaua reală, SUMO are intersecții, semafoare și virări pe care automatul nu le are. Diferențele n-ar mai spune nimic despre model. Pe coridorul drept, singura diferență rămasă e regula de mers (Krauss față de NaSch). Rețeaua din OSM e bună pentru o figură de context.

## Ce aveți de făcut

Tot ce e marcat TODO în kit:

- [ ] `RingRoad.step` (NaSch, VDR, slow-to-start) și diagrama fundamentală pe inel;
- [ ] coridorul cu mai multe benzi, intrare și ieșire;
- [ ] controllerul MAPE-K și pragurile lui, alese din diagrama fundamentală;
- [ ] `run_one` și experimentele;
- [ ] **timpul de revenire după incident**: definiți-l o singură dată și calculați-l la fel pe automat și pe `sumo_speed.csv`. Scriptul nu îl calculează intenționat: definit diferit, comparația n-ar mai avea sens;
- [ ] diagrama fundamentală SUMO peste cea a automatului, comentată în raport;
- [ ] vizualizarea: `vizualizare/sablon/coridor.html` arată coridorul de sus și diagrama spațiu-timp. Exportați grila din `Corridor` la fiecare pas (formatul e în `exemplu_coridor.py`), câte un fișier pe variantă. Detalii în `vizualizare/README.md`, secțiunea P1.

## La ce să vă așteptați

- **Capacitatea diferă mult.** O bandă SUMO duce cam 1800–2000 veh/h; NaSch cu p = 0,3 și celule de 7,5 m, cam 1250. La aceeași cerere, SUMO stă departe de capacitate și automatul nu. Nu e o greșeală de implementare; calibrarea lui p (și a lui p0 la VDR) e de obicei discuția cea mai importantă despre realism.
- **Primul tronson e mereu mai dens**, pentru că vehiculele intră acolo cu viteza limitată de spațiul liber. Dacă pragurile controllerului se aplică și acolo, îl va vedea „aglomerat” aproape tot timpul.
- **VDR și slow-to-start au capacitate mai mică decât NaSch.** Un controller care trece pe ele la aglomerare poate „îmbunătăți” timpul de parcurs doar pentru că ține vehiculele la intrare. Raportați și `wait_mean`, altfel efectul nu se vede.

## Întrebări frecvente

**`find_binary` nu găsește sumo.** Activați mediul din kit; dacă tot nu merge, `pip install eclipse-sumo` sau setați `SUMO_HOME` către o instalare oficială.

**Vreau 3 benzi.** Schimbați `model.lanes` în config. Rețeaua se reface la fiecare rulare.

**Scriptul durează mult.** Fiecare rulare SUMO e ~10 s; diagrama fundamentală adaugă 3 rulări. Pentru teste, `--runs 1`.
