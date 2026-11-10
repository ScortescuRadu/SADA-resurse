# Notă de proiectare: P1, trafic urban cu automate celulare

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
| M | densitate [veh/km/bandă] și viteză [km/h] pe tronsoane de ... m, la fiecare ... s |
| A | liber / aglomerat / blocat; praguri de intrare ... și de ieșire ... |
| P | regula (sau p, vmax) pe tronson, pentru fiecare regim: ... |
| E | `set_rule` la pasul următor, fără oprire |
| K | regimul anterior, pragurile, jurnalul |

<Diagrama: din `raport/latex/main.tex` (figura e deja desenată) sau din `docs/MAPEK.md` (Mermaid).>

## 4. Ce avem deja

<Ce rulează, cu un număr sau o figură: de exemplu rezultatul unui test, o curbă, o comparație preliminară.>

## 5. Planul de experimente

| Scenariu | Variante comparate | Metrica principală | Rulări | Ce rezultat ar confirma ipoteza |
|---|---|---|---|---|
| cerere_scazuta | fix_nasch, fix_vdr, fix_sts, adaptiv | ... | 20 | ... |
| cerere_medie | fix_nasch, fix_vdr, fix_sts, adaptiv | ... | 20 | ... |
| cerere_ridicata | fix_nasch, fix_vdr, fix_sts, adaptiv | ... | 20 | ... |
| incident | fix_nasch, fix_vdr, fix_sts, adaptiv | ... | 20 | ... |

Referința (fără adaptare): `fix_nasch`.

## 6. Riscuri și întrebări

<Ce nu știți încă și ce ați face dacă nu merge. Întrebările pentru cadrul didactic.>
