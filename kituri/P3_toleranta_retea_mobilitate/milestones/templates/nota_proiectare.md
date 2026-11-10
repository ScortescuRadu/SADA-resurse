# Notă de proiectare: P3, toleranță ierarhică la defectare

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
| M | muchiile căzute de la ultimul ciclu; componentele conexe |
| A | perechile afectate; tipul defectului |
| P | nivelul (1, 2, 3) pentru fiecare pereche afectată |
| E | ruta curentă actualizată; serviciu degradat |
| K | rutele principale și de rezervă, muchiile critice, jurnalul |

<Diagrama: din `raport/latex/main.tex` (figura e deja desenată) sau din `docs/MAPEK.md` (Mermaid).>

## 4. Ce avem deja

<Ce rulează, cu un număr sau o figură: de exemplu rezultatul unui test, o curbă, o comparație preliminară.>

## 5. Planul de experimente

| Scenariu | Variante comparate | Metrica principală | Rulări | Ce rezultat ar confirma ipoteza |
|---|---|---|---|---|
| aleator | fara_recuperare, doar_nivel2, nivele_1_3 | ... | 20 | ... |
| tintit | fara_recuperare, doar_nivel2, nivele_1_3 | ... | 20 | ... |
| inundatie | fara_recuperare, doar_nivel2, nivele_1_3 | ... | 20 | ... |
| rauri | fara_recuperare, doar_nivel2, nivele_1_3 | ... | 20 | ... |
| central | fara_recuperare, doar_nivel2, nivele_1_3 | ... | 20 | ... |

Referința (fără adaptare): `fara_recuperare`.

## 6. Riscuri și întrebări

<Ce nu știți încă și ce ați face dacă nu merge. Întrebările pentru cadrul didactic.>
