# Ghid de implementare: P2, algoritm genetic cu condiții care se schimbă

Ghidul urmează pașii din fișa proiectului și îi leagă de fișierele din kit. Ordinea e recomandată; dacă aveți o idee mai bună, discutați-o la laborator.

Etapele cu predare (săptămânile 3, 5, 9, 12, 14) au fiecare un fișier în [`milestones/`](milestones/README.md), cu ce trebuie să aveți, codul care vă ajută și ce citiți atunci. Termenii din articole sunt traduși în [`docs/GLOSAR.md`](docs/GLOSAR.md).

## Calendar orientativ

| Săptămâna | Ce ar trebui să aveți |
|---|---|
| 1–2 | mediul instalat, exemplul de jucărie rulat, instanțele de dezvoltare generate; ramura aleasă |
| 3 | pașii 1–3: fitness, optimul exact, referințele simple; tema confirmată |
| 4–5 | pasul 4 (algoritmul genetic static); nota de proiectare |
| 6–8 | pașii 5–6: schimbările și controllerul |
| 9 | **prototip**: algoritmul detectează o schimbare și reacționează, vizibil în jurnal și în figura de convergență |
| 10–11 | pașii 7–8: experimentele complete și varianta cu două obiective |
| 12 | varianta de lucru a raportului |
| 13–14 | figuri finale, prezentare, verificarea reproductibilității |

## Problema, pe scurt

Avem n intervenții, fiecare cu un cost c_i, un beneficiu b_i și un scor de echitate e_i. Alegem un vector x ∈ {0,1}^n care maximizează w_b · Σ b_i x_i + w_e · Σ e_i x_i cu Σ c_i x_i ≤ B. E problema rucsacului, cu ponderi. La ramura B, x_i sunt numere întregi (ore-vehicul pe linie), iar beneficiul fiecărei linii crește din ce în ce mai încet.

Partea „dinamică”: în timpul rulării, problema se schimbă (B scade, o intervenție dispare, ponderile se modifică). Soluția bună de până atunci poate deveni proastă sau chiar nefezabilă.

---

## Pasul 1. Funcția de fitness

**Unde:** `src/sada/p2/ga.py`, metoda `DynamicGA.fitness`. Restul problemei e gata în `problem.py`: `objective(x)`, `total_cost(x)`, `violations(x)`, `is_feasible(x)`.

Două variante, alegeți una și justificați-o:

- **Penalizare:** `objective(x) − λ · depășire`. Simplu, dar λ trebuie ales: prea mic și cele mai bune soluții sunt nefezabile, prea mare și algoritmul evită granița bugetului, unde sunt de obicei soluțiile bune. O penalizare proporțională cu depășirea, cu λ cel puțin cât cel mai bun raport beneficiu/cost, e un punct de pornire.
- **Reparare:** cât timp soluția depășește bugetul, scoateți elementul cu cel mai mic raport valoare/cost (sau unul aleator dintre cele mai slabe). Garantează fezabilitatea. Spuneți dacă scrieți individul reparat înapoi în populație.

Indiferent de variantă, metricile se raportează pe **cea mai bună soluție fezabilă**, nu pe cel mai mare fitness.

## Pasul 2. Optimul exact

**Unde:** `src/sada/p2/exact.py` (gata) și `scripts/solve_optima.py`.

```bash
python scripts/solve_optima.py data/dev/dev_A_20.json data/dev/changes_dev_A_20.json
```

Calculează optimul pentru fiecare stare a problemei (înainte și după fiecare schimbare) și îl salvează în `results/optima_<nume>.json`. Pentru n = 20 durează sub o secundă. Testul `test_exact_matches_bruteforce` confirmă că rezultatul e corect pe o instanță mică.

## Pasul 3. Referințele simple

**Unde:** `src/sada/p2/baselines.py` (gata).

- `greedy(problem)` sortează după valoare/cost și adaugă cât încape.
- `random_search(problem, n_evals, rng)` încearcă n_evals soluții aleatoare.

Ambele întorc și numărul de evaluări. **Comparați algoritmii la același număr de evaluări ale funcției obiectiv**, nu la același număr de generații: o generație de 80 de indivizi înseamnă 80 de evaluări.

Strategia lacomă e o referință surprinzător de bună pentru problema rucsacului. Dacă algoritmul genetic nu o depășește, e un rezultat de discutat, nu de ascuns.

## Pasul 4. Algoritmul genetic static

**Unde:** `DynamicGA.init_population` și `DynamicGA.next_generation`.

Bucla `run` e scrisă. Voi scrieți:

- **Inițializarea:** biți aleatori cu probabilitatea buget/cost total (aproximativ), ca o parte din populație să fie fezabilă de la început.
- **Selecția prin turnir:** alegeți k indivizi la întâmplare, câștigă cel cu fitness-ul cel mai mare. Cu k = 2–3 presiunea de selecție e moderată.
- **Încrucișarea uniformă** (fiecare genă de la un părinte ales aleator) sau într-un punct, cu probabilitatea p_crossover.
- **Mutația:** fiecare bit se inversează cu probabilitatea `self.p_mut` (implicit 1/n). Folosiți atributul, nu o constantă, pentru că controllerul îl modifică.
- **Elitismul:** cei mai buni `elitism` indivizi trec neschimbați.

Varianta NumPy, pentru o pereche de părinți `a`, `b`:

```python
mask = self.rng.random(n) < 0.5            # încrucișare uniformă
a[mask], b[mask] = b[mask], a[mask].copy()
flip = self.rng.random(n) < self.p_mut     # mutație
a[flip] = 1 - a[flip]
```

La ramura B (întreg), mutația adaugă sau scade câteva ore-vehicul pe o linie și le mută de pe alta, iar repararea readuce totalul la buget.

**Cum verificați:** `pytest -q` (testul `test_ga_beats_random_on_small` trebuie să treacă). Pe `dev_A_20`, fără schimbări, algoritmul ar trebui să ajungă aproape de optimul exact în câteva zeci de generații.

## Pasul 5. Schimbările

**Unde:** `src/sada/p2/dynamic.py` (gata). `ChangeSchedule.apply` e apelat de `run` la începutul fiecărei generații.

Algoritmul **nu** primește niciun semnal. Schimbarea se vede doar prin faptul că aceeași soluție are acum alt fitness. Rulați algoritmul static pe `dev_A_20` cu schimbările și desenați cel mai bun individ pe generații: veți vedea căderile și cât de greu revine. Aceasta e referința „fără adaptare”.

## Pasul 6. Detecția și răspunsul (MAPE-K)

**Unde:** `src/sada/p2/controller.py`. Pentru structură, uitați-vă întâi la `examples/toy_mapek.py` și la `docs/MAPEK.md`.

| Etapă | Ce face concret |
|---|---|
| M | cel mai bun, media, diversitatea (`ga.diversity()`); fitness-ul santinelelor, reevaluate |
| A | „schimbare” dacă fitness-ul vreunei santinele s-a modificat (`sentinel_changed`); „stagnare” dacă cel mai bun nu s-a îmbunătățit de `stagnation_generations`; altfel „normal” |
| P | la schimbare: răspunsul configurat; la stagnare: eventual imigranți; altfel nimic |
| E | modifică `ga.p_mut`, apelează `ga.replace_random(frac)`, repornește parțial |
| K | santinelele și fitness-ul lor, arhiva soluțiilor bune, momentul ultimei schimbări, jurnalul |

**Santinelele.** La prima generație alegeți 3–5 indivizi și păstrați-i separat (nu fac parte din populație). La fiecare generație îi reevaluați; dacă fitness-ul unuia diferă de valoarea anterioară, problema s-a schimbat. Reevaluarea costă evaluări: adunați-le la `ga.evaluations`, ca să comparați corect.

**Răspunsurile** (comparați cel puțin două):

- **hipermutație:** `p_mut × hypermutation_factor` pentru `hypermutation_generations` generații, apoi revine la `base_p_mut`;
- **imigranți aleatori:** `ga.replace_random(immigrants_frac)` la schimbare (sau la fiecare generație, varianta clasică);
- **repornire parțială:** reinițializați `restart_frac` din populație, păstrând elita și arhiva.

**Arhiva.** Soluțiile bune de dinainte pot redeveni bune (de exemplu dacă bugetul revine). O arhivă mică, din care reintroduceți câțiva indivizi după schimbare, e o îmbunătățire ușor de testat.

**Cum verificați:** `python scripts/plot_convergence.py data/dev/dev_A_20.json data/dev/changes_dev_A_20.json`. Figura arată cele două variante, optimul exact pe fiecare interval și momentele schimbărilor. Varianta cu controller trebuie să revină mai repede. Jurnalul controllerului trebuie să conțină o linie pentru fiecare schimbare detectată.

## Pasul 7. Experimentele

**Unde:** `src/sada/p2/experiments.py` (`run_one`; `recovery_generations` e gata), apoi `scripts/run_all.py`.

**Metrici:**

- `final_ratio`: cea mai bună soluție fezabilă la final, împărțită la optimul stării finale;
- `recovery_gen_mean`: media, pe schimbări, a numărului de generații până la 95% din noul optim;
- `evaluations`: numărul total de evaluări (inclusiv santinelele).

Pentru instanțele mari (n = 40), optimul exact nu se poate calcula. Folosiți cea mai bună soluție găsită în câteva rulări lungi (de exemplu 10 rulări × 5000 de generații, pe problema din fiecare stare) și spuneți în raport că reperul e „cea mai bună soluție cunoscută”, nu optimul.

**Experimentele minime din fișă:**

- algoritmul genetic, strategia lacomă și căutarea aleatoare, pe aceeași problemă;
- pentru n ≤ 20: abaterea față de optimul exact;
- cel puțin două schimbări în timpul rulării, cu numărul de generații până la 95% din noul optim;
- varianta cu două obiective, cu NSGA-II și hipervolumul;
- cel puțin 30 de rulări pe configurație.

## Pasul 8. Două obiective (NSGA-II)

**Unde:** `src/sada/p2/moo.py`. Completați `_evaluate`:

```python
b, e = problem.objectives(x.astype(int))
out["F"] = [-b, -e]                                    # pymoo minimizează
out["G"] = [problem.total_cost(x.astype(int)) - problem.budget]
```

`run_nsga2` întoarce frontul (`res.X`, `res.F`). Desenați-l (beneficiu pe x, echitate pe y) și calculați hipervolumul cu `hypervolume(res.F, ref_point)`. Punctul de referință trebuie să fie **același în toate rulările**; de exemplu `[0, 0]` (beneficiu și echitate nule, cu minus). Raportați media ± abaterea hipervolumului pe 30 de rulări.

O întrebare bună pentru discuție: unde se află pe front soluția găsită de algoritmul cu o singură funcție obiectiv ponderată, pentru diferite ponderi?

---

## Greșeli frecvente

- **Comparații pe număr de generații** în loc de număr de evaluări.
- **Soluții care depășesc bugetul raportate ca rezultat.** Verificați fezabilitatea la final, mai ales cu penalizare.
- **Controller care „știe” când apare schimbarea** (citește direct `ChangeSchedule`). Controllerul vede doar ce măsoară.
- **Santinele nereevaluate** sau reevaluări necontorizate.
- **Punct de referință diferit pentru hipervolum** între rulări.
- **Beneficii prezentate ca măsurate.** Sunt estimări de model.

## Întrebări de verificare înainte de prezentare

- Ce face funcția de fitness cu o soluție care depășește bugetul și de ce ați ales așa?
- Cum detectează algoritmul o schimbare? Ce se întâmplă dacă schimbarea nu afectează santinelele?
- De ce ajută hipermutația și când strică?
- De ce comparați la același număr de evaluări?
- Ce înseamnă hipervolumul și de ce contează punctul de referință?
