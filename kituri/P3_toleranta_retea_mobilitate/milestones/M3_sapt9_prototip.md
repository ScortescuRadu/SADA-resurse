# M3 (săptămâna 9): prototipul

## Ce predați

Cod care rulează cap-coadă și arată o primă adaptare, demonstrat la laborator. Nu trebuie să fie frumos și nici complet; trebuie să se vadă controllerul luând cel puțin o decizie ca urmare a unei perturbări. O echipă fără prototip în săptămâna 9 discută cu cadrul didactic un plan realist pentru timpul rămas.

## Ce trebuie să aveți până atunci

Codul pentru pasul 6 (cele trei nivele ca buclă MAPE-K); pasul 7 (bucla Langton) pornit:

- [ ] `HierarchicalRecovery` lucrează pe `NetworkState` și scrie în jurnal nivelul care a rezolvat fiecare pereche.
- [ ] `pytest -q tests/test_m3_prototip.py` trece.
- [ ] `python scripts/demo_prototip.py --group <scenariu>` produce harta cu muchiile căzute și rutele de rezervă.
- [ ] Bucla Langton rulează în `scripts/run_ca.py` și coincide cu Golly la câțiva pași.
- [ ] Deciziile apar în jurnal (`results/logs/*.jsonl`) și le puteți explica una câte una.

## Demonstrația

Rulați `python scripts/demo_prototip.py --group <scenariu>`: ponderea perechilor servite înainte, imediat după defect și după recuperare, plus harta `results/figures/demo_p3_map.pdf`.

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

- Byl (1989) și, opțional, Sayama (1999) pentru variantele buclei.
- Pentru lucrări conexe: proceedings AHS și ICES, „self-repair” și „hierarchical fault tolerance”.
- `docs/STATISTICA.md` din kit, înainte să porniți rulările repetate.

## Greșeli tipice

- Controllerul există, dar nu decide nimic în scenariul demonstrației (pragurile sunt prea sus sau perturbarea prea mică). Verificați înainte, cu seed fix.
- Controllerul „știe” când vine perturbarea (citește direct scenariul). El vede doar ce măsoară.
- Demonstrația pornește de la zero și durează 10 minute. Pregătiți un scenariu scurt, cu seed fix, care arată decizia în primul minut.
