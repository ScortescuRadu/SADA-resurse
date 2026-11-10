# M2 (săptămâna 5): nota de proiectare

## Ce predați

Două pagini: obiectivul, datele folosite, diagrama MAPE-K completată și planul de experimente. Model: [templates/nota_proiectare.md](templates/nota_proiectare.md). Nu se notează separat, dar e baza pe care primiți feedback.

## Ce trebuie să aveți până atunci

Codul pentru pașii 1–4 din GHID.md (fitness, optimul exact, referințele, algoritmul static):

- [ ] `DynamicGA.fitness`, `init_population`, `next_generation` implementate; `pytest -q tests/test_p2_problem.py` trece fără teste sărite.
- [ ] Pe `dev_A_20` fără schimbări: algoritmul static ajunge aproape de optim; notați după câte evaluări.
- [ ] Comparația la același număr de evaluări cu strategia lacomă și căutarea aleatoare.
- [ ] Decizia penalizare vs. reparare, cu un argument.
- [ ] Diagrama MAPE-K schițată, cu valori concrete (nu „monitorizează sistemul”, ci ce, cât de des, în ce unități).

## La ce întrebări răspunde nota

- Cum tratați bugetul (penalizare sau reparare) și de ce?
- Cum detectați schimbarea: câte santinele, cum le alegeți, cât costă în evaluări?
- Ce răspunsuri comparați (cel puțin două) și ce așteptați de la fiecare?
- Cum măsurați revenirea la 95% din noul optim pentru instanțele unde optimul exact nu se poate calcula?

## Planul de experimente

Configurația din kit are deja scenariile (`dev_A_20`, `dev_A_40`) și variantele (`greedy`, `aleator`, `ag_static`, `ag_hipermut`, `ag_imigranti`), cu 30 de rulări pe combinație. În notă le confirmați sau le schimbați, cu motivul. Un plan bun spune, pentru fiecare experiment: ce întrebare are, ce compară, ce metrică, câte rulări, ce rezultat ar confirma ipoteza și ce rezultat ar infirma-o.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| testele pașilor de până acum | `pytest -q` |
| explorarea datelor, cu numerele pentru notă | `notebooks/01_explorare.ipynb` |
| diagrama MAPE-K în Mermaid sau TikZ | `docs/MAPEK.md`, `raport/latex/main.tex` (figura e deja desenată, cu textele temei) |
| verificarea etapei | `python scripts/milestone_check.py M2` |

## Ce citiți acum

- Cobb (1990) pentru hipermutație și Grefenstette (1992) pentru imigranții aleatori: ideea, nu toate detaliile.
- Branke (2002), capitolul despre detecția schimbărilor și memorie.
- `docs/STATISTICA.md` din kit: de ce comparați la același număr de evaluări și pe aceleași seed-uri.

## Greșeli tipice

- Nota descrie tema din fișă în loc de proiectul vostru. Cadrul didactic știe tema; vrea să afle deciziile voastre.
- Planul de experimente fără referință („testăm controllerul”). Fiecare experiment are o variantă cu care se compară.
- Diagrama MAPE-K generică. Dacă diagrama ar putea fi a oricărei teme, nu e încă gata.
