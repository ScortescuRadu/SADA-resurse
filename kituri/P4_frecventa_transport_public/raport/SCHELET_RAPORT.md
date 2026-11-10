# Schelet de raport

Structura e cea obligatorie din fișă. Șablonul LaTeX gata de folosit e în `raport/latex/` (compilați cu `latexmk -pdf main.tex` sau încărcați folderul pe Overleaf). Scrieți direct în șablonul IEEE sau ACM (de exemplu pe Overleaf); fișierul acesta vă ajută doar să știți ce intră în fiecare secțiune. Lungimea totală: 8–12 pagini fără anexe, A4, text de 11 pt, predat ca PDF.

---

**Titlu.** Spune ce sistem și ce adaptare, nu doar domeniul. „Selecția adaptivă a regulilor într-un automat celular de trafic urban” e mai bun decât „Trafic cu automate celulare”.

## Rezumat (150–200 de cuvinte)

Patru-cinci propoziții: problema, ce ați construit, cum ați testat, cel puțin un rezultat numeric, ce înseamnă. Îl scrieți ultimul.

## 1. Introducere (aprox. 1 pagină)

- Contextul: de ce contează problema, în două-trei propoziții.
- Ce lipsește: ce nu fac soluțiile fixe sau existente.
- Obiectivul proiectului.
- Contribuțiile, ca listă scurtă și verificabilă („un controller care...”, „o comparație pe 3 regimuri de cerere...”).

## 2. Lucrări conexe (1–1,5 pagini)

Minimum 6 referințe, dintre care cel puțin 2 din conferințele indicate în fișă. Grupate pe idei, nu enumerate (vedeți `docs/LUCRARI_CONEXE.md`).

## 3. Sistemul propus (2–3 pagini)

- Modelul (ce simulează, ce reprezintă un pas, ce unități).
- Algoritmii, cu pseudocod dacă ajută.
- **Diagrama MAPE-K** cu elementele concrete ale proiectului (vedeți `docs/MAPEK.md`).
- Parametrii, într-un tabel, și justificarea fiecăruia (din literatură, din date, din experimente preliminare).

## 4. Date și configurare (aprox. 1 pagină)

- Sursele datelor (cu licență) și cum le-ați pregătit.
- Seed-urile, numărul de rulări, perioada de încălzire.
- Hardware și versiuni de software (din `requirements.lock.txt`).
- Comanda care reface experimentele.

## 5. Rezultate (2–3 pagini)

- Comparația cu cel puțin o variantă de referință (fără adaptare).
- Tabele cu medie ± abatere standard (`results/tables/summary.tex`).
- Grafice cu axe etichetate, unități, legendă și un titlu care spune ce se măsoară.
- Fiecare tabel și fiecare figură sunt comentate în text: ce se vede și ce înseamnă.
- Cel puțin o figură care arată adaptarea în timp (perturbarea și reacția).

## 6. Discuție și limite (aprox. 1 pagină)

Ce arată rezultatele, ce nu arată și ce ar trebui verificat în continuare. Exemple de limite care trebuie spuse când e cazul: datele sunt estimări de model; un singur coridor sau o singură rețea; pragurile reglate pe aceleași date; simplificări ale modelului.

## 7. Concluzii (jumătate de pagină)

Ce s-a obținut, cu un număr, și ce rămâne deschis.

## Referințe

Format uniform, IEEE sau ACM.

## Anexă

- Declarația privind instrumentele folosite (`raport/DECLARATIE_INSTRUMENTE.md`).
- Comanda de rulare.
- Tabele extinse.
