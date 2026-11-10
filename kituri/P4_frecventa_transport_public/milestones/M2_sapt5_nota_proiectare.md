# M2 (săptămâna 5): nota de proiectare

## Ce predați

Două pagini: obiectivul, datele folosite, diagrama MAPE-K completată și planul de experimente. Model: [templates/nota_proiectare.md](templates/nota_proiectare.md). Nu se notează separat, dar e baza pe care primiți feedback.

## Ce trebuie să aveți până atunci

Codul pentru pașii 1–3 din GHID.md (feed-ul, S0, încărcările):

- [ ] S0 calculat (`python scripts/baseline_s0.py`): curse, intervale, ore-vehicul pe linie.
- [ ] `TransitSystem.from_files` implementat; gradul de încărcare pe linie și fereastră.
- [ ] Verificat că în S0 există linii peste 85% și sub 30%.
- [ ] Ipotezele scrise: timpul de întoarcere la capăt, cererea inelastică, ce se întâmplă la închiderea unei linii.
- [ ] Diagrama MAPE-K schițată, cu valori concrete (nu „monitorizează sistemul”, ci ce, cât de des, în ce unități).

## La ce întrebări răspunde nota

- Ce linii ați ales și de ce (moduri, zona cu acces slab)?
- Cum ați calculat orele-vehicul și ce ați presupus despre întoarcerea la capăt?
- Ce funcție de fitness folosește algoritmul genetic și cu ce ponderi?
- Ce intervale maxime impuneți, ca nicio linie să nu rămână fără serviciu?

## Planul de experimente

Configurația din kit are deja scenariile (`s0_normal`, `inchidere_linie`, `cerere_zona_20`) și variantele (`orar_fix`, `regula`, `alg_genetic`), cu 20 de rulări pe combinație. În notă le confirmați sau le schimbați, cu motivul. Un plan bun spune, pentru fiecare experiment: ce întrebare are, ce compară, ce metrică, câte rulări, ce rezultat ar confirma ipoteza și ce rezultat ar infirma-o.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| testele pașilor de până acum | `pytest -q` |
| explorarea datelor, cu numerele pentru notă | `notebooks/01_explorare.ipynb` |
| diagrama MAPE-K în Mermaid sau TikZ | `docs/MAPEK.md`, `raport/latex/main.tex` (figura e deja desenată, cu textele temei) |
| verificarea etapei | `python scripts/milestone_check.py M2` |

## Ce citiți acum

- Ceder (2007): metodele bazate pe încărcarea maximă (punct de pornire pentru regula simplă).
- Documentația `scipy.spatial.cKDTree` (pentru acoperire, pasul 6).
- `docs/MAPEK.md` din kit.

## Greșeli tipice

- Nota descrie tema din fișă în loc de proiectul vostru. Cadrul didactic știe tema; vrea să afle deciziile voastre.
- Planul de experimente fără referință („testăm controllerul”). Fiecare experiment are o variantă cu care se compară.
- Diagrama MAPE-K generică. Dacă diagrama ar putea fi a oricărei teme, nu e încă gata.
