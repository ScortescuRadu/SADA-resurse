# M1 (săptămâna 3): tema și echipa

## Ce predați

Un mesaj către cadrul didactic, până la sfârșitul săptămânii 3, cu tema, numele membrilor. Model: [templates/mesaj_tema.md](templates/mesaj_tema.md).

## Ce trebuie să aveți până atunci

- [ ] Mediul instalat (`bash setup/setup.sh` sau `setup\setup.ps1`) și `python scripts/check_env.py` fără probleme la pachete.
- [ ] `python examples/toy_mapek.py` rulat; înțelegeți ce fac cele patru metode ale controllerului.
- [ ] Un depozit Git cu conținutul kitului, la care au acces ambii membri (`docs/GIT_SI_MEDIU.md`).
- [ ] Copiați graful din pachet în `data/p3_retea/` și rulați `python scripts/inspect_graph.py ...`.
- [ ] Rulați `notebooks/01_explorare.ipynb`: structura rețelei și primul experiment de vulnerabilitate.
- [ ] Instalați Golly și deschideți bucla Langton din `Patterns/Loops/`; urmăriți o replicare.
- [ ] Primele trei articole găsite și notate în două-trei rânduri fiecare.

## De ce contează alegerea acum

Tema e confirmată în săptămâna 3, iar nota de proiectare vine două săptămâni mai târziu. Dacă după explorarea datelor tema nu vă convinge, acum e momentul să schimbați, nu în săptămâna 6.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| verificarea mediului | `python scripts/check_env.py` |
| exemplul de buclă MAPE-K | `python examples/toy_mapek.py` |
| explorarea datelor | `notebooks/01_explorare.ipynb` (în VS Code sau `pip install jupyterlab` și `jupyter lab`) |
| verificarea etapei | `python scripts/milestone_check.py M1` |

## Ce citiți acum

- Albert, Jeong și Barabási (2000): scurt, figurile cu eliminarea aleatoare vs. țintită.
- Langton (1984): secțiunea care descrie bucla și ciclul de replicare.
- Tutorialul NetworkX: https://networkx.org/documentation/stable/tutorial.html
- `docs/LUCRARI_CONEXE.md` din kit: cum căutați și cum notați articolele.

## Greșeli tipice

- Instalarea amânată „până avem nevoie”. Problemele de mediu (Python vechi, PATH, PowerShell) se rezolvă ușor la laborator, greu cu o zi înainte de prototip.
- Un singur membru are codul. Faceți depozitul comun din prima săptămână.
