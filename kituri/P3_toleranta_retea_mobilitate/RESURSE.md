# Resurse pentru P3

Verificați datele bibliografice în baza de date a bibliotecii înainte de a le prelua în raport.

## Articole de pornire

- R. Albert, H. Jeong, A.-L. Barabási, *Error and attack tolerance of complex networks*, Nature 406, 2000. doi:10.1038/35019019. Diferența dintre defecte aleatoare și atacuri țintite.
- P. Holme, B. J. Kim, C. N. Yoon, S. K. Han, *Attack vulnerability of complex networks*, Physical Review E 65, 056109, 2002. doi:10.1103/PhysRevE.65.056109. Atacuri după grad și după intermediere, cu și fără recalculare.
- C. G. Langton, *Self-reproduction in cellular automata*, Physica D 10(1–2), 1984. doi:10.1016/0167-2789(84)90256-2. Bucla Langton.
- J. Byl, *Self-reproduction in small cellular automata*, Physica D 34, 1989. Bucla Byl, mai mică.
- G. Boeing, *OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks*, Computers, Environment and Urban Systems 65, 2017. De citat dacă folosiți OSMnx.
- A. Hagberg, D. Schult, P. Swart, *Exploring network structure, dynamics, and function using NetworkX*, SciPy 2008.

## Sisteme autoadaptive și toleranță la defectare

- J. O. Kephart, D. M. Chess, *The vision of autonomic computing*, IEEE Computer 36(1), 2003. doi:10.1109/MC.2003.1160055. Buclele MAPE-K și „self-healing”.
- Proceedings AHS (Adaptive Hardware and Systems) și ICES (International Conference on Evolvable Systems): căutați „fault tolerance”, „self-repair”, „hierarchical fault tolerance”.

## Unde căutați lucrări conexe

- Google Scholar: „road network vulnerability”, „transport network resilience flooding”, „k-shortest disjoint paths rerouting”.
- Pentru reziliența rețelelor de transport: lucrările de trecere în revistă despre „vulnerability” și „resilience” ale rețelelor rutiere.
- Pentru autoreplicare: proceedings ALIFE (https://direct.mit.edu/isal), „self-replicating loops”.

## Documentație și unelte

- NetworkX: https://networkx.org/documentation/stable/ (drumuri minime, `edge_disjoint_paths`, `edge_betweenness_centrality`, `restricted_view`)
- OSMnx: https://osmnx.readthedocs.io
- Golly: https://golly.sourceforge.io (rulare, reguli, modele de autoreplicare)

## Tutoriale practice

- NetworkX, tutorialul oficial: https://networkx.org/documentation/stable/tutorial.html
- Exemplele OSMnx (notebook-uri): https://github.com/gboeing/osmnx-examples
- Golly, ghidul pentru reguli (Help → Rule Tables în program) și modelele din Patterns/Loops.

## Pe etape

Fiecare fișier din `milestones/` are o secțiune „Ce citiți acum”, cu lecturile potrivite momentului. Bibliografia de mai sus există și în format BibTeX, în `raport/latex/refs.bib`.

## Ce citiți întâi

1. Albert, Jeong și Barabási (2000): scurt și foarte citat.
2. Documentația NetworkX pentru drumuri minime pe grafuri ponderate.
3. Langton (1984), secțiunea care descrie bucla și ciclul de replicare.
4. `docs/MAPEK.md` din acest kit.
