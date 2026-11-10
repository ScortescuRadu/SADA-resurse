# M3 (săptămâna 9): prototipul

## Ce predați

Cod care rulează cap-coadă și arată o primă adaptare, demonstrat la laborator. Nu trebuie să fie frumos și nici complet; trebuie să se vadă controllerul luând cel puțin o decizie ca urmare a unei perturbări. O echipă fără prototip în săptămâna 9 discută cu cadrul didactic un plan realist pentru timpul rămas.

## Ce trebuie să aveți până atunci

Codul pentru pașii 4–6 (regula simplă, algoritmul genetic, acoperirea); algoritmul genetic poate fi încă simplificat:

- [ ] `SimpleRuleController` respectă bugetul și intervalul maxim.
- [ ] `coverage_share` implementat.
- [ ] `pytest -q tests/test_m3_prototip.py` trece.
- [ ] `python scripts/demo_prototip.py` (cu datele voastre; `--synthetic` doar pentru testarea controllerului) produce harta termică.
- [ ] Deciziile apar în jurnal (`results/logs/*.jsonl`) și le puteți explica una câte una.

## Demonstrația

Rulați `python scripts/demo_prototip.py`: lista deciziilor pe ferestre, verificarea bugetului și harta termică `results/figures/demo_p4_heatmap.pdf`, orar fix vs. controller.

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

- Pentru lucrări conexe: GECCO, „transit frequency setting genetic algorithm”; Google Scholar, „dynamic headway control”.
- Validatorul GTFS, dacă feed-ul are probleme: https://gtfs-validator.mobilitydata.org
- `docs/STATISTICA.md` din kit, înainte să porniți rulările repetate.

## Greșeli tipice

- Controllerul există, dar nu decide nimic în scenariul demonstrației (pragurile sunt prea sus sau perturbarea prea mică). Verificați înainte, cu seed fix.
- Controllerul „știe” când vine perturbarea (citește direct scenariul). El vede doar ce măsoară.
- Demonstrația pornește de la zero și durează 10 minute. Pregătiți un scenariu scurt, cu seed fix, care arată decizia în primul minut.
