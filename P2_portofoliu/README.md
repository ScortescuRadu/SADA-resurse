# P2. Portofoliu de intervenții: resurse

## Pe scurt

Primiți un portofoliu realist de 40 de intervenții pentru Timișoara, cu bugetul și scenariile de schimbare, în formatul din kit. Primiți și optimul exact pentru orice mărime (kitul se oprește la n = 24) și frontul Pareto exact pentru varianta cu două obiective. Instanțele sintetice din `data/dev/` rămân pentru teste.

## Instalare

Din folderul de resurse, cu mediul din kit activat:

```bash
python instaleaza.py P2 ../repo_nostru
```

Ce apare în repo:

| Fișier | La ce folosește |
|---|---|
| `data/p2_portofoliu/tm_A_40.json` | 40 de intervenții, cost total 17,5 mil. EUR, buget 6,1 mil. EUR |
| `data/p2_portofoliu/tm_A_20.json` | 20 dintre ele (jumătate din fiecare tip), buget 40% din costul lor |
| `data/p2_portofoliu/changes_tm_A_*.json` | schimbările: −30% buget (g 100), o intervenție devine imposibilă (g 200), ponderi 50/50 (g 300) |
| `data/p2_portofoliu/changes_tm_A_*_revenire.json` | altă variantă: −30%, bugetul revine, −30% (bun pentru a testa memoria) |
| `data/raw/timisoara/` | populația, stațiile și cartierele din care s-a construit portofoliul |
| `src/sada/p2/problem.py` | **înlocuiește** fișierul din kit: același cod, plus interacțiunile dintre intervenții |
| `src/sada/p2/exact.py` | **înlocuiește** fișierul din kit: căutarea exhaustivă de acolo, plus MILP și programare dinamică |
| `src/sada/p2/front_exact.py` | frontul Pareto exact, ca reper pentru NSGA-II |
| `scripts/solve_optima.py` | **înlocuiește** scriptul din kit: merge și pentru n = 40 |
| `scripts/build_portfolio.py` | reface portofoliul din `data/raw/timisoara/` |

Fișierele care înlocuiesc ceva din kit sunt compatibile cu el: instanțele `dev/` și testele din kit merg la fel. Dacă le modificaserăți, versiunile voastre rămân ca `*.inainte_de_resurse`.

În `config/default.yaml` se adaugă:
- scenariile `tm_A_20` și `tm_A_40`, lângă `dev_A_20` și `dev_A_40`;
- secțiunea `portfolio`, cu parametrii modelului de date.

## Primii pași

**1. Verificați instalarea:**

```bash
python ../SADA_resurse_studenti/verifica.py P2 .
```

Trebuie să vedeți, printre altele, `optimul exact al stării inițiale: 377.49`.

**2. Calculați optimul exact pentru fiecare stare a problemei:**

```bash
python scripts/solve_optima.py data/p2_portofoliu/tm_A_20.json data/p2_portofoliu/changes_tm_A_20.json
python scripts/solve_optima.py data/p2_portofoliu/tm_A_40.json data/p2_portofoliu/changes_tm_A_40.json
python scripts/solve_optima.py data/p2_portofoliu/tm_A_40.json data/p2_portofoliu/changes_tm_A_40_revenire.json
```

Fiecare durează sub o secundă și scrie `results/optima_<scenariu>.json`. Pentru `tm_A_40` trebuie să iasă 377,49 → 324,61 → 243,16 → 172,58. Numele fișierului vine din fișierul de schimbări, deci varianta `_revenire` nu o suprascrie pe cea standard (scriptul din kit le numea după instanță).

**3. Uitați-vă la date înainte să scrieți algoritmul.** De exemplu:

```python
import json, pandas as pd
d = json.load(open("data/p2_portofoliu/tm_A_40.json"))
df = pd.DataFrame(d["items"])
df["raport"] = df.benefit / df.cost
print(df.groupby("type")[["cost", "benefit", "equity", "raport"]].mean())
```

## Formatul instanțelor

E cel din `DATE.md`, cu trei câmpuri în plus pe care `problem.py` din kit le ignoră:

- `type`, `lon`, `lat` (și `line`, la benzile de biciclete): tipul și locația, pentru o hartă a portofoliului;
- `population`: câți locuitori are zona de influență a intervenției;
- `interactions`: listă de `{"i", "j", "benefit", "equity"}`. Dacă finanțați și `i`, și `j`, se scad aceste valori din beneficiu și echitate, pentru că cele două acoperă parțial aceeași populație.

Cu `problem.py` din resurse, obiectivul ține cont de interacțiuni: `problem.objective(x)` le scade automat, iar `problem.has_interactions` spune dacă instanța le are.

## Unelte

**Optimul exact**, pentru orice instanță binară, inclusiv cu interacțiuni și dependențe:

```python
from sada.p2.exact import solve, solve_milp, solve_integer_dp
x, v = solve(problem)      # alege singur: enumerare (n ≤ 16), MILP (binar), programare dinamică (ramura B)
```

Optimul exact elimină „cea mai bună soluție cunoscută” din GHID, pasul 7: abaterea față de optim e reală și la n = 40.

**Frontul Pareto exact** (beneficiu, echitate), ca să aveți cu ce compara hipervolumul NSGA-II:

```python
from sada.p2.front_exact import exact_front, eps_front
F = exact_front(problem)   # n ≤ 24, prin enumerare
F = eps_front(problem)     # orice n, prin ε-constrângere iterativă cu MILP
from sada.p2.moo import hypervolume
hv_exact = hypervolume(-F, [0, 0])           # aceeași convenție ca în kit: obiectivele cu minus
```

Raportați raportul `HV(NSGA-II) / HV(front exact)`; e mult mai ușor de interpretat decât un hipervolum absolut.

## Ce aveți de făcut

Tot ce e marcat TODO în kit:

- [ ] `DynamicGA.fitness`: penalizare sau reparare, cu justificare;
- [ ] `init_population`, `next_generation`: turnir, încrucișare, mutație, elitism;
- [ ] `DynamicGAController`: detecția schimbării și cel puțin două răspunsuri;
- [ ] `PortfolioProblem._evaluate` în `moo.py`, pentru NSGA-II;
- [ ] `run_one`, experimentele (30 de rulări pe configurație), analiza;
- [ ] comparația cu lacomul și cu căutarea aleatoare, la același număr de evaluări;
- [ ] vizualizarea: intervențiile pe harta din `vizualizare/sablon/index.html`, cele alese aprinse, generație cu generație. Detalii în `vizualizare/README.md`, secțiunea P2.

## La ce să vă așteptați

- **Lacomul e foarte bun pe instanțele astea.** Un rucsac cu multe elemente mici e cazul în care strategia lacomă e aproape optimă. Dacă algoritmul vostru abia o depășește, nu e neapărat ceva greșit; spuneți asta în raport și căutați unde diferă.
- **Penalizare sau reparare: alegerea contează mult.** Încercați-le pe amândouă înainte să vă hotărâți asupra răspunsului la schimbare; una dintre ele schimbă cât de util e restul controllerului.
- **Santinelele.** Indivizii aleatori nu observă neapărat orice tip de schimbare. Încercați fiecare tip pe rând (buget, element eliminat, ponderi) și verificați că le detectați pe toate.
- **Eroarea offline** (media pe generații a distanței față de optimul curent; Branke, 2002) e metrica standard în optimizarea dinamică. Prinde și căderea, și revenirea, într-un singur număr. Merită raportată lângă cele din fișă.
- **Frontul exact are puncte pe care optimizarea ponderată nu le găsește** (cele care nu sunt pe înfășurătoarea convexă). E un răspuns bun la întrebarea din GHID, pasul 8.

## Întrebări frecvente

**Pot să schimb portofoliul?** Da. Parametrii sunt în secțiunea `portfolio` din config: costurile unitare, efectele pe tip, bugetul, redundanța. Rulați `python scripts/build_portfolio.py`, apoi refaceți optimele. Spuneți în raport ce ați schimbat.

**`scipy.optimize.milp` nu există.** Aveți nevoie de SciPy ≥ 1.9: `pip install -U scipy`.

**Merge și pentru ramurile B și C?** `solve` alege programarea dinamică pentru ramura B (întreg) și respectă dependențele de la C. Portofoliul din Timișoara e însă doar pentru ramura A.
