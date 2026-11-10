# M4 (săptămâna 12): varianta de lucru a raportului

## Ce predați

Raportul complet ca structură: toate secțiunile au conținut, iar rezultatele pot fi provizorii, marcate ca atare. E ultima ocazie de feedback pe text înainte de predare.

## Ce trebuie să aveți până atunci

- [ ] Referința SUMO rulată: diagrama fundamentală din detectoare, pe același coridor.
- [ ] `run_one` complet: cele trei regimuri de cerere și incidentul, toate variantele.
- [ ] Rularea completă cu 20 de seed-uri; `make_figures.py` și `report_numbers.py`.
- [ ] Raportul în șablonul din `raport/latex/` (sau IEEE/ACM pe Overleaf), cu toate cele 7 secțiuni.
- [ ] Minimum 6 referințe, dintre care cel puțin 2 din GECCO, AHS, ICES, ALife sau ECAL, în `refs.bib`.
- [ ] Autoevaluarea completată: [templates/autoevaluare_raport.md](templates/autoevaluare_raport.md).

## De la rezultate la text

```bash
python scripts/estimate_runtime.py        # cât durează rularea completă
python scripts/run_all.py                 # toate rulările -> results/results.csv
python scripts/make_figures.py            # boxplot-uri, results/tables/summary.tex
python scripts/report_numbers.py          # diferențe, p, A12 -> results/tables/comparisons.md
cd raport/latex && latexmk -pdf main.tex  # tabelul și figurile se iau direct din results/
```

`comparisons.md` vă dă, pentru fiecare scenariu și metrică, propoziția aproape gata: „Pe scenariul X, varianta adaptivă reduce timpul mediu de parcurs cu Y% față de referință (Mann–Whitney, p = …, A12 = …)”.

## Figurile pe care le așteptăm

- diagrama spațiu-timp (inel sau o bandă din coridor)
- diagrama fundamentală CA vs. SUMO
- boxplot-urile timpului de parcurs pe scenarii
- viteza pe tronsonul incidentului în timp, fix vs. adaptiv, cu deciziile marcate

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| șablonul LaTeX, cu diagrama MAPE-K și bibliografia de pornire | `raport/latex/main.tex`, `raport/latex/refs.bib` |
| scheletul în Markdown (ce intră în fiecare secțiune) | `raport/SCHELET_RAPORT.md` |
| numerele pentru secțiunea de rezultate | `scripts/report_numbers.py` |
| verificarea etapei | `python scripts/milestone_check.py M4` |

## Ce citiți acum

- `docs/LUCRARI_CONEXE.md`: cum grupați lucrările conexe pe idei.
- `docs/STATISTICA.md`: semnificație statistică vs. mărimea efectului.
- 2–3 articole din conferințele indicate, pentru stilul secțiunii de rezultate.

## Greșeli tipice

- Rezultate fără referință sau fără abatere standard.
- Figuri cu axe fără unități, sau copiate cu capturi de ecran.
- Secțiunea de limite lipsă sau formală. Spuneți concret ce nu arată experimentele.
- Rularea completă pornită în săptămâna 12. Estimați timpul din săptămâna 10 (`estimate_runtime.py`).
