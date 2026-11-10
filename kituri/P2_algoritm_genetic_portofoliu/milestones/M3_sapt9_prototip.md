# M3 (săptămâna 9): prototipul

## Ce predați

Cod care rulează cap-coadă și arată o primă adaptare, demonstrat la laborator. Nu trebuie să fie frumos și nici complet; trebuie să se vadă controllerul luând cel puțin o decizie ca urmare a unei perturbări. O echipă fără prototip în săptămâna 9 discută cu cadrul didactic un plan realist pentru timpul rămas.

## Ce trebuie să aveți până atunci

Codul pentru pașii 5–6 (schimbările și controllerul):

- [ ] `DynamicGAController` cu santinele și cel puțin un răspuns funcțional.
- [ ] Evaluarea santinelelor e contorizată în `ga.evaluations`.
- [ ] `pytest -q tests/test_m3_prototip.py` trece (detecție în 3 generații, fără alarme false, hipermutația revine).
- [ ] `python scripts/demo_prototip.py` și `python scripts/plot_convergence.py ...` produc figurile.
- [ ] Deciziile apar în jurnal (`results/logs/*.jsonl`) și le puteți explica una câte una.

## Demonstrația

Rulați `python scripts/demo_prototip.py`: lista arată generația fiecărei schimbări și reacția controllerului. Apoi arătați `results/figures/convergence.pdf` (`scripts/plot_convergence.py`): varianta statică vs. cea cu controller, cu optimul exact pe fiecare interval.

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

- Documentația pymoo pentru probleme binare și NSGA-II (pasul 8): https://pymoo.org/getting_started/index.html
- Pentru lucrări conexe: proceedings GECCO, căutați „dynamic knapsack” și „change detection evolutionary”.
- `docs/STATISTICA.md` din kit, înainte să porniți rulările repetate.

## Greșeli tipice

- Controllerul există, dar nu decide nimic în scenariul demonstrației (pragurile sunt prea sus sau perturbarea prea mică). Verificați înainte, cu seed fix.
- Controllerul „știe” când vine perturbarea (citește direct scenariul). El vede doar ce măsoară.
- Demonstrația pornește de la zero și durează 10 minute. Pregătiți un scenariu scurt, cu seed fix, care arată decizia în primul minut.
