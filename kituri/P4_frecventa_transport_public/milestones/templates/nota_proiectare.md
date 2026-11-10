# Notă de proiectare: P4, frecvența transportului public

**Echipa:** <nume>  **Data:** <...>

*(Maximum două pagini. Înlocuiți tot ce e între < > și toate „...”.)*

## 1. Obiectiv

<Două-trei propoziții: ce construiți, ce decide controllerul, ce ipoteză testați. Exemplu de formă: „Ipoteza: dacă ..., atunci ... față de varianta fără adaptare, mai ales când ...”.>

## 2. Date

| Fișier | Sursă | Ce folosim din el | Probleme găsite |
|---|---|---|---|
| ... | pachetul disciplinei / descărcat la ... | ... | ... |

## 3. Bucla MAPE-K

| Pas | În proiectul nostru |
|---|---|
| M | gradul de încărcare pe linie, la fiecare 15 minute |
| A | linii peste 85%, sub 30% |
| P | noua alocare (regula simplă / algoritmul genetic: ...) |
| E | curse noi pe linie în fereastra următoare, bugetul constant |
| K | S0, alocările anterioare, zonele |

<Diagrama: din `raport/latex/main.tex` (figura e deja desenată) sau din `docs/MAPEK.md` (Mermaid).>

## 4. Ce avem deja

<Ce rulează, cu un număr sau o figură: de exemplu rezultatul unui test, o curbă, o comparație preliminară.>

## 5. Planul de experimente

| Scenariu | Variante comparate | Metrica principală | Rulări | Ce rezultat ar confirma ipoteza |
|---|---|---|---|---|
| s0_normal | orar_fix, regula, alg_genetic | ... | 20 | ... |
| inchidere_linie | orar_fix, regula, alg_genetic | ... | 20 | ... |
| cerere_zona_20 | orar_fix, regula, alg_genetic | ... | 20 | ... |

Referința (fără adaptare): `orar_fix`.

## 6. Riscuri și întrebări

<Ce nu știți încă și ce ați face dacă nu merge. Întrebările pentru cadrul didactic.>
