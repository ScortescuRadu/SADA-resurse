# P4. Controller pentru frecvența transportului public

Kit de pornire pentru proiectul de semestru la **Sisteme autoadaptive. Design și aplicații**.

Construiți un controller care, la fiecare 15 minute simulate, citește încărcarea a 10–15 linii de transport public și mută curse de pe liniile goale pe cele aglomerate, în limita flotei. Alocarea se calculează cu un algoritm genetic și se compară cu o regulă simplă și cu orarul real neschimbat, pornind de la feed-ul GTFS al operatorului local.

## Ce găsiți aici

| Fișier / folder | Pentru ce |
|---|---|
| `GHID.md` | **Începeți de aici.** Pașii de implementare, cu fișierele implicate și cum verificați fiecare pas |
| `milestones/` | Etapele (săptămânile 3, 5, 9, 12, 14): ce predați, ce trebuie să aveți, codul și lecturile pentru fiecare etapă, șabloane |
| `DATE.md` | Feed-ul GTFS, încărcările, capacitățile, zonele; descărcare și citare |
| `RESURSE.md` | Articole, specificația GTFS, biblioteci |
| `setup/` | Instalare pentru Linux/macOS/WSL (`setup.sh`) și Windows (`setup.ps1`) |
| `config/default.yaml` | Feed-ul, ziua, fereastra, liniile alese, pragurile, scenariile, variantele |
| `src/sada/p4/` | `gtfs_io.py`, `baseline.py` sunt gata; `controller.py`, `ga_alloc.py`, `coverage.py`, `experiments.py` au părți TODO |
| `scripts/` | descărcarea feed-ului, inspecția, orarul S0, experimentele, figurile |
| `examples/toy_mapek.py` | Exemplu complet de buclă MAPE-K pe un sistem de jucărie |
| `notebooks/01_explorare.ipynb` | Explorarea datelor pentru primele etape; rulează și fără datele din pachet |
| `raport/latex/` | Șablonul LaTeX al raportului (IEEE pe Overleaf), cu diagrama MAPE-K a temei și bibliografia de pornire |
| `tests/` | `pytest -q`, cu un feed GTFS minuscul de test în `tests/fixtures/` |
| `docs/`, `raport/`, `prezentare/` | ghiduri scurte, schelete, liste de verificare |

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
bash setup/setup.sh                       # Windows: powershell -ExecutionPolicy Bypass -File setup\setup.ps1
source .venv/bin/activate                 # Windows: .\.venv\Scripts\Activate.ps1
python scripts/check_env.py
python examples/toy_mapek.py
python scripts/download_gtfs.py           # sau copiați feed-ul din pachet în data/raw/gtfs/
python scripts/inspect_gtfs.py            # alegeți o zi lucrătoare și liniile -> config
python scripts/baseline_s0.py             # orarul de referință S0
pytest -q
```

## Comanda care reface tot

```bash
python scripts/run_all.py              # scenarii × variante × seed-uri -> results/results.csv
python scripts/make_figures.py         # boxplot-uri și tabele cu medie ± abatere
```

## Ce e gata și ce faceți voi

Gata: descărcarea feed-ului, citirea GTFS (inclusiv orele după miezul nopții și excepțiile de calendar), selecția unei zile, cursele din fereastra de vârf, intervalele și orele-vehicul pe linie, proiecția stațiilor în metri, infrastructura de experimente și statistică.

Voi: legarea încărcărilor de linii, regula simplă, alocarea prin algoritm genetic, acoperirea populației, perturbările, experimentele, analiza, raportul.
