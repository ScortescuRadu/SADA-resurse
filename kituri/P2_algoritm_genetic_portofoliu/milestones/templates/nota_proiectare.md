# Notă de proiectare: P2, algoritm genetic pentru portofoliu

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
| M | cel mai bun, media, diversitatea; ... santinele reevaluate la fiecare generație |
| A | schimbare (santinelele își schimbă fitness-ul), stagnare (... generații fără îmbunătățire) |
| P | răspunsul: ... |
| E | p_mut × ... pentru ... generații / ...% imigranți / ... |
| K | santinele, arhiva de ... soluții, jurnalul |

<Diagrama: din `raport/latex/main.tex` (figura e deja desenată) sau din `docs/MAPEK.md` (Mermaid).>

## 4. Ce avem deja

<Ce rulează, cu un număr sau o figură: de exemplu rezultatul unui test, o curbă, o comparație preliminară.>

## 5. Planul de experimente

| Scenariu | Variante comparate | Metrica principală | Rulări | Ce rezultat ar confirma ipoteza |
|---|---|---|---|---|
| dev_A_20 | greedy, aleator, ag_static, ag_hipermut, ag_imigranti | ... | 30 | ... |
| dev_A_40 | greedy, aleator, ag_static, ag_hipermut, ag_imigranti | ... | 30 | ... |

Referința (fără adaptare): `ag_static`.

## 6. Riscuri și întrebări

<Ce nu știți încă și ce ați face dacă nu merge. Întrebările pentru cadrul didactic.>
