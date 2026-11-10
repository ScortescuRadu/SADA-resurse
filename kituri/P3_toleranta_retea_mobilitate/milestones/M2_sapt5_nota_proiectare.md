# M2 (săptămâna 5): nota de proiectare

## Ce predați

Două pagini: obiectivul, datele folosite, diagrama MAPE-K completată și planul de experimente. Model: [templates/nota_proiectare.md](templates/nota_proiectare.md). Nu se notează separat, dar e baza pe care primiți feedback.

## Ce trebuie să aveți până atunci

Codul pentru pașii 1–5 din GHID.md (graful, perechile OD, rutele de rezervă, importanța, defectele):

- [ ] Perechile OD fixate (`python scripts/prepare_od.py`) și salvate.
- [ ] `backup_route`, `precompute` și cele trei tipuri de defect implementate.
- [ ] Curba „perechi conectate vs. muchii eliminate”, aleator și țintit, fără recuperare.
- [ ] Numărul de perechi fără rută de rezervă.
- [ ] Diagrama MAPE-K schițată, cu valori concrete (nu „monitorizează sistemul”, ci ce, cât de des, în ce unități).

## La ce întrebări răspunde nota

- Ce definiți ca „pas de simulare” și cum măsurați timpul de recuperare?
- Ruta de rezervă poate folosi sensul opus al aceleiași străzi? De ce?
- Ce face nivelul 3 cu capacitatea rămasă (ce presupuneți)?
- Ce parte a buclei Langton comparați cu refacerea rutei și cum o perturbați?

## Planul de experimente

Configurația din kit are deja scenariile (`aleator`, `tintit`, `inundatie`, `rauri`, `central`) și variantele (`fara_recuperare`, `doar_nivel2`, `nivele_1_3`), cu 20 de rulări pe combinație. În notă le confirmați sau le schimbați, cu motivul. Un plan bun spune, pentru fiecare experiment: ce întrebare are, ce compară, ce metrică, câte rulări, ce rezultat ar confirma ipoteza și ce rezultat ar infirma-o.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| testele pașilor de până acum | `pytest -q` |
| explorarea datelor, cu numerele pentru notă | `notebooks/01_explorare.ipynb` |
| diagrama MAPE-K în Mermaid sau TikZ | `docs/MAPEK.md`, `raport/latex/main.tex` (figura e deja desenată, cu textele temei) |
| verificarea etapei | `python scripts/milestone_check.py M2` |

## Ce citiți acum

- Holme et al. (2002): atacuri cu și fără recalcularea importanței (decizia `recompute`).
- Documentația NetworkX pentru `restricted_view`, `edge_disjoint_paths`, `edge_betweenness_centrality`.
- `docs/MAPEK.md` din kit, pentru diagrama cu trei nivele.

## Greșeli tipice

- Nota descrie tema din fișă în loc de proiectul vostru. Cadrul didactic știe tema; vrea să afle deciziile voastre.
- Planul de experimente fără referință („testăm controllerul”). Fiecare experiment are o variantă cu care se compară.
- Diagrama MAPE-K generică. Dacă diagrama ar putea fi a oricărei teme, nu e încă gata.
