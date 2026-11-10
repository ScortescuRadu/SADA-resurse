# P3. Toleranță ierarhică la defectare pe o rețea de mobilitate

Kit de pornire pentru proiectul de semestru la **Sisteme autoadaptive. Design și aplicații**.

Construiți un sistem de recuperare pe trei nivele pentru o rețea rutieră de 500–3000 de noduri: detecție, comutare pe rute de rezervă precalculate și degradare controlată, cu servirea perechilor prioritare. Muchiile cad izolat, țintit sau în grup (inundație, traversări de râu). În paralel, implementați o buclă Langton (sau Byl) care se autoreplică și o comparați cu refacerea unei rute.

## Ce găsiți aici

| Fișier / folder | Pentru ce |
|---|---|
| `GHID.md` | **Începeți de aici.** Pașii de implementare, cu fișierele implicate și cum verificați fiecare pas |
| `milestones/` | Etapele (săptămânile 3, 5, 9, 12, 14): ce predați, ce trebuie să aveți, codul și lecturile pentru fiecare etapă, șabloane |
| `DATE.md` | Graful, populația, scenariile de defect, regulile automatului celular și de unde le luați |
| `RESURSE.md` | Articole, documentație, unelte |
| `setup/` | Instalare pentru Linux/macOS/WSL (`setup.sh`) și Windows (`setup.ps1`) |
| `config/default.yaml` | Căile datelor, perechile OD, defectele, scenariile și variantele |
| `src/sada/p3/` | `graph_io.py`, `od.py`, `metrics.py`, `ca.py` sunt gata; `routes.py`, `failures.py`, `recovery.py`, `experiments.py` au părți TODO |
| `scripts/` | descărcarea rețelei, inspecția grafului, perechile OD, importanța muchiilor, automatul celular, experimentele, figurile |
| `examples/toy_mapek.py` | Exemplu complet de buclă MAPE-K pe un sistem de jucărie |
| `notebooks/01_explorare.ipynb` | Explorarea datelor pentru primele etape; rulează și fără datele din pachet |
| `raport/latex/` | Șablonul LaTeX al raportului (IEEE pe Overleaf), cu diagrama MAPE-K a temei și bibliografia de pornire |
| `tests/` | `pytest -q`; testul pentru ruta de rezervă e sărit până o implementați |
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
# după ce copiați pachetul de date în data/p3_retea/ și ajustați data.graph în config:
python scripts/inspect_graph.py data/p3_retea/<graf>.graphml
python scripts/prepare_od.py
pytest -q
```

## Comanda care reface tot

```bash
python scripts/run_all.py              # scenarii × variante × seed-uri -> results/results.csv
python scripts/make_figures.py         # boxplot-uri și tabele cu medie ± abatere
```

## Ce e gata și ce faceți voi

Gata: citirea și verificarea grafului, eșantionarea perechilor OD, calculul rapid al costurilor OD și al conectivității, importanța muchiilor, motorul de automat celular cu reguli Golly (@TABLE) și modele RLE, numărarea structurilor, descărcarea rețelei din OSM, infrastructura de experimente și statistică.

Voi: rutele de rezervă, cele trei tipuri de defect, recuperarea pe nivele ca buclă MAPE-K, experimentele, rularea și analiza buclei Langton, secțiunea de comparație, raportul.
