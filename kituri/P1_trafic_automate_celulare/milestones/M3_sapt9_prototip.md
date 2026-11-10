# M3 (săptămâna 9): prototipul

## Ce predați

Cod care rulează cap-coadă și arată o primă adaptare, demonstrat la laborator. Nu trebuie să fie frumos și nici complet; trebuie să se vadă controllerul luând cel puțin o decizie ca urmare a unei perturbări. O echipă fără prototip în săptămâna 9 discută cu cadrul didactic un plan realist pentru timpul rămas.

## Ce trebuie să aveți până atunci

Codul pentru pașii 5–6 (coridorul și controllerul); pasul 7 (SUMO) poate fi încă în lucru:

- [ ] `Corridor` cu 2–3 benzi, intrare și ieșire deschise, tronsoane, incident.
- [ ] `TrafficController` cu histerezis; pragurile completate în `config/default.yaml`.
- [ ] `pytest -q tests/test_m3_prototip.py` trece.
- [ ] `python scripts/demo_prototip.py` produce jurnalul și figura cu viteza pe tronsonul incidentului.
- [ ] Deciziile apar în jurnal (`results/logs/*.jsonl`) și le puteți explica una câte una.

## Demonstrația

Rulați `python scripts/demo_prototip.py` și arătați figura `results/figures/demo_p1_timeline.pdf`: banda gri e incidentul, liniile roșii sunt deciziile controllerului. Spuneți dinainte ce trebuie să se vadă (de exemplu: „tronsonul 5 trece în regim blocat, controllerul trece pe VDR, după incident revine”).

Pentru orice măsurătoare din jurnal: `python scripts/plot_decisions.py results/logs/<fișier>.jsonl --key <cheie>` (fără `--key` afișează cheile disponibile). Pentru o curbă continuă, porniți controllerul cu `log_every_step=True`.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| demonstrația | `scripts/demo_prototip.py` |
| testele de acceptanță ale prototipului | `pytest -q tests/test_m3_prototip.py` (sărite până implementați piesele) |
| figura cu adaptarea în timp | `sada.timeline.plot_timeline`, `scripts/plot_decisions.py` |
| estimarea timpului pentru experimentul complet | `python scripts/estimate_runtime.py` (după ce `run_one` merge) |
| verificarea etapei | `python scripts/milestone_check.py M3` |

## Ce citiți acum

- Documentația SUMO pentru detectoare E1 și TraCI (linkurile din `RESURSE.md`): veți avea nevoie de ele imediat după prototip.
- Pentru ideea de control: căutați „variable speed limit cellular automaton” în Google Scholar; 2–3 articole sunt suficiente pentru lucrările conexe.
- `docs/STATISTICA.md` din kit, înainte să porniți rulările repetate.

## Greșeli tipice

- Controllerul există, dar nu decide nimic în scenariul demonstrației (pragurile sunt prea sus sau perturbarea prea mică). Verificați înainte, cu seed fix.
- Controllerul „știe” când vine perturbarea (citește direct scenariul). El vede doar ce măsoară.
- Demonstrația pornește de la zero și durează 10 minute. Pregătiți un scenariu scurt, cu seed fix, care arată decizia în primul minut.
