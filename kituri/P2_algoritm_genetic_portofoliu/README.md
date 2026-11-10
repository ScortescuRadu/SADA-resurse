# P2. Algoritm genetic pentru un portofoliu de intervenții, cu condiții care se schimbă

Kit de pornire pentru proiectul de semestru la **Sisteme autoadaptive. Design și aplicații**.

Un oraș nu poate finanța toate intervențiile propuse. Construiți un algoritm genetic care alege portofoliul cel mai bun în limita bugetului, în timp ce problema se schimbă fără avertisment (bugetul scade, o intervenție devine imposibilă, se schimbă ponderea dintre beneficiu și echitate). Algoritmul trebuie să observe singur schimbarea și să se adapteze.

## Ce găsiți aici

| Fișier / folder | Pentru ce |
|---|---|
| `GHID.md` | **Începeți de aici.** Pașii de implementare, cu fișierele implicate și cum verificați fiecare pas |
| `milestones/` | Etapele (săptămânile 3, 5, 9, 12, 14): ce predați, ce trebuie să aveți, codul și lecturile pentru fiecare etapă, șabloane |
| `DATE.md` | Formatul datelor, instanțele de dezvoltare, ramurile A, B, C |
| `RESURSE.md` | Articole, biblioteci, tutoriale |
| `setup/` | Instalare pentru Linux/macOS/WSL (`setup.sh`) și Windows (`setup.ps1`) |
| `config/default.yaml` | Parametrii algoritmului, ai controllerului, scenariile și variantele |
| `src/sada/p2/` | `problem.py`, `exact.py`, `baselines.py`, `dynamic.py` sunt gata; `ga.py`, `controller.py`, `moo.py`, `experiments.py` au părți TODO |
| `scripts/` | generarea instanțelor de dezvoltare, optimul exact, figura de convergență, rularea experimentelor, figurile |
| `examples/toy_mapek.py` | Exemplu complet de buclă MAPE-K pe un sistem de jucărie |
| `notebooks/01_explorare.ipynb` | Explorarea datelor pentru primele etape; rulează și fără datele din pachet |
| `raport/latex/` | Șablonul LaTeX al raportului (IEEE pe Overleaf), cu diagrama MAPE-K a temei și bibliografia de pornire |
| `tests/` | `pytest -q`; testul pentru algoritmul genetic e sărit până îl implementați |
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
python examples/toy_mapek.py              # cum arată o buclă MAPE-K completă
python scripts/prepare_data.py            # instanțe sintetice de dezvoltare în data/dev/
python scripts/solve_optima.py data/dev/dev_A_20.json data/dev/changes_dev_A_20.json
pytest -q
```

## Comanda care reface tot

După ce completați părțile TODO:

```bash
python scripts/run_all.py              # scenarii × variante × 30 de seed-uri -> results/results.csv
python scripts/make_figures.py         # boxplot-uri și tabele cu medie ± abatere
```

Test rapid: `python scripts/run_all.py --set experiment.n_runs=2`.

## Ce e gata și ce faceți voi

Gata: citirea problemei, obiectivul și verificarea constrângerilor, aplicarea schimbărilor, optimul exact pentru n ≤ 24, strategia lacomă, căutarea aleatoare, bucla principală a algoritmului genetic cu cârligele pentru controller, calculul timpului de revenire, rularea NSGA-II și hipervolumul, infrastructura de experimente și statistică.

Voi: funcția de fitness (penalizare sau reparare), operatorii genetici, detecția schimbării și răspunsul (MAPE-K), problema cu două obiective, experimentele, analiza, raportul.
