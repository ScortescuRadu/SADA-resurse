# M2 (săptămâna 5): nota de proiectare

## Ce predați

Două pagini: obiectivul, datele folosite, diagrama MAPE-K completată și planul de experimente. Model: [templates/nota_proiectare.md](templates/nota_proiectare.md). Nu se notează separat, dar e baza pe care primiți feedback.

## Ce trebuie să aveți până atunci

Codul pentru pașii 1–4 din GHID.md (inelul, diagrama spațiu-timp, diagrama fundamentală, VDR și slow-to-start):

- [ ] `RingRoad.step` implementat; `pytest -q tests/test_p1_nasch.py` trece fără teste sărite.
- [ ] Diagrama fundamentală pentru cele trei reguli (`python scripts/fundamental_diagram.py`); notați densitatea critică și fluxul maxim.
- [ ] Pragurile controllerului propuse, în veh/km/bandă, pornind de la densitatea critică.
- [ ] Scenariile de cerere alese în raport cu capacitatea coridorului (benzi × fluxul maxim).
- [ ] Diagrama MAPE-K schițată, cu valori concrete (nu „monitorizează sistemul”, ci ce, cât de des, în ce unități).

## La ce întrebări răspunde nota

- Ce măsurați pe tronson (densitate, viteză) și la ce interval? De ce intervalul acela?
- Ce praguri despart regimurile liber / aglomerat / blocat și cum ați evitat oscilațiile?
- Ce regulă (sau ce parametri) alege controllerul în fiecare regim și ce ipoteză testați prin asta?
- Ce metrică e principală (timpul de parcurs?) și cum o măsurați fără perioada de încălzire?

## Planul de experimente

Configurația din kit are deja scenariile (`cerere_scazuta`, `cerere_medie`, `cerere_ridicata`, `incident`) și variantele (`fix_nasch`, `fix_vdr`, `fix_sts`, `adaptiv`), cu 20 de rulări pe combinație. În notă le confirmați sau le schimbați, cu motivul. Un plan bun spune, pentru fiecare experiment: ce întrebare are, ce compară, ce metrică, câte rulări, ce rezultat ar confirma ipoteza și ce rezultat ar infirma-o.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| testele pașilor de până acum | `pytest -q` |
| explorarea datelor, cu numerele pentru notă | `notebooks/01_explorare.ipynb` |
| diagrama MAPE-K în Mermaid sau TikZ | `docs/MAPEK.md`, `raport/latex/main.tex` (figura e deja desenată, cu textele temei) |
| verificarea etapei | `python scripts/milestone_check.py M2` |

## Ce citiți acum

- Barlović et al. (1998): VDR și stările metastabile. Uitați-vă la figura cu histerezisul.
- Maerivoet și De Moor (2005): secțiunea despre modelele cu mai multe benzi (pentru coridor).
- `docs/MAPEK.md` din kit: capcanele (oscilații, controller care „trișează”).

## Greșeli tipice

- Nota descrie tema din fișă în loc de proiectul vostru. Cadrul didactic știe tema; vrea să afle deciziile voastre.
- Planul de experimente fără referință („testăm controllerul”). Fiecare experiment are o variantă cu care se compară.
- Diagrama MAPE-K generică. Dacă diagrama ar putea fi a oricărei teme, nu e încă gata.
