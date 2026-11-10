# P1. Trafic urban cu automate celulare care își schimbă regulile

Kit de pornire pentru proiectul de semestru la **Sisteme autoadaptive. Design și aplicații**.

Construiți un automat celular pentru un coridor urban de 3–5 km, cu 2–3 benzi, care își alege singur regula de rulare (Nagel–Schreckenberg, VDR, slow-to-start) în funcție de starea traficului. Același coridor se simulează în SUMO, ca referință.

## Ce găsiți aici

| Fișier / folder | Pentru ce |
|---|---|
| `GHID.md` | **Începeți de aici.** Pașii de implementare, în ordine, cu ce fișier atinge fiecare pas și cum verificați că merge |
| `milestones/` | Etapele (săptămânile 3, 5, 9, 12, 14): ce predați, ce trebuie să aveți, codul și lecturile pentru fiecare etapă, șabloane |
| `DATE.md` | Ce date folosiți, de unde le luați, cum le descărcați și cum le citați |
| `RESURSE.md` | Articole, documentație, tutoriale |
| `setup/` | Scripturi de instalare pentru Linux/macOS/WSL (`setup.sh`) și Windows (`setup.ps1`) |
| `config/default.yaml` | Toți parametrii, scenariile și variantele într-un singur loc |
| `src/sada/` | Codul. `mapek.py`, `experiment.py`, `stats.py` sunt gata; `p1/` conține ce aveți de completat (marcat cu TODO) |
| `scripts/` | Descărcare OSM, construirea rețelei SUMO, cererea, diagrame, rularea experimentelor, figuri |
| `examples/toy_mapek.py` | Un exemplu complet de buclă MAPE-K pe un sistem de jucărie; rulează din prima |
| `notebooks/01_explorare.ipynb` | Explorarea datelor pentru primele etape; rulează și fără datele din pachet |
| `raport/latex/` | Șablonul LaTeX al raportului (IEEE pe Overleaf), cu diagrama MAPE-K a temei și bibliografia de pornire |
| `tests/` | Teste care vă spun când o piesă e corectă (`pytest -q`) |
| `docs/` | Ghiduri scurte: mediul de lucru și Git, statistică, proiectarea buclei MAPE-K, lucrări conexe |
| `raport/`, `prezentare/` | Scheletul raportului, lista de verificare, modelul de declarație, scheletul prezentării |

## Unelte pe etape

| Script | Etapa | Ce face |
|---|---|---|
| `scripts/milestone_check.py M1..M5` | toate | verifică ce lipsește pentru etapa respectivă |
| `scripts/demo_prototip.py` | M3 | demonstrația pentru prototip (jurnal + figură) |
| `scripts/plot_decisions.py` | M3–M5 | o măsurătoare din jurnal, cu deciziile controllerului marcate |
| `scripts/estimate_runtime.py` | M3–M4 | cât durează experimentul complet |
| `scripts/report_numbers.py` | M4 | diferențe, p și A12 pentru secțiunea de rezultate |
| `scripts/verify_submission.py` | M5 | verificarea finală pe o copie curată a depozitului |

## Pornire rapidă

```bash
# 1. instalare (o singură dată)
bash setup/setup.sh                                   # Linux / macOS / WSL / Git Bash
# powershell -ExecutionPolicy Bypass -File setup\setup.ps1   # Windows

# 2. în fiecare terminal nou
source .venv/bin/activate                             # Windows: .\.venv\Scripts\Activate.ps1

# 3. verificați că totul e instalat
python scripts/check_env.py

# 4. vedeți cum arată o buclă MAPE-K completă
python examples/toy_mapek.py

# 5. testele (cele pentru RingRoad sunt sărite până le implementați)
pytest -q
```

SUMO se instalează automat din pip (pachetul `eclipse-sumo`), împreună cu `netconvert`, `netedit` și `sumo-gui`. Dacă preferați instalarea oficială (https://sumo.dlr.de/docs/Downloads.php), setați variabila `SUMO_HOME`.

## Comanda care reface tot

După ce ați completat părțile marcate cu TODO:

```bash
python scripts/run_all.py          # toate scenariile × variantele × 20 de seed-uri -> results/results.csv
python scripts/make_figures.py     # boxplot-uri și tabele cu medie ± abatere -> results/
```

Pentru un test rapid: `python scripts/run_all.py --set experiment.n_runs=2`.

Această comandă trebuie să apară și în README-ul pe care îl predați. Adaptați fișierul acesta la final: ștergeți ce nu folosiți, descrieți ce ați adăugat.

## Ce e gata și ce faceți voi

Gata: instalarea, citirea configurației, clasa de bază `Controller` (MAPE-K cu jurnal), rularea grilei de experimente cu seed-uri, statistica (medie, abatere, IC 95%, Mann–Whitney, A12), figurile generice, descărcarea OSM, construirea rețelei SUMO, generarea cererii, detectoarele E1 și rularea prin TraCI, diagrama fundamentală și diagrama spațiu-timp (după ce implementați modelul).

Voi: regulile automatului (`RingRoad.step`), coridorul cu mai multe benzi, controllerul, experimentele, analiza, raportul. Adică tot ce se notează.
