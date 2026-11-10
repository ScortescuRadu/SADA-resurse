# Resurse pentru P1

Verificați datele bibliografice în baza de date a bibliotecii înainte de a le prelua în raport.

## Articole de pornire

- K. Nagel, M. Schreckenberg, *A cellular automaton model for freeway traffic*, Journal de Physique I 2(12), 1992. doi:10.1051/jp1:1992277. Articolul original al modelului.
- M. Maerivoet, B. De Moor, *Cellular automata models of road traffic*, Physics Reports 419(1), 2005. doi:10.1016/j.physrep.2005.08.005. Trecere în revistă foarte completă; aici găsiți VDR, slow-to-start și multe alte variante, plus modele cu mai multe benzi.
- R. Barlović, L. Santen, A. Schadschneider, M. Schreckenberg, *Metastable states in cellular automata for traffic flow*, European Physical Journal B 5, 1998. Articolul care introduce VDR.
- M. Takayasu, H. Takayasu, *1/f noise in a traffic model*, Fractals 1(4), 1993. Una dintre primele reguli slow-to-start.
- P. A. Lopez et al., *Microscopic traffic simulation using SUMO*, IEEE ITSC, 2018. doi:10.1109/ITSC.2018.8569938. Referința de citat pentru SUMO.

## Sisteme autoadaptive

- J. O. Kephart, D. M. Chess, *The vision of autonomic computing*, IEEE Computer 36(1), 2003. doi:10.1109/MC.2003.1160055. Originea buclei MAPE-K.
- M. Salehie, L. Tahvildari, *Self-adaptive software: landscape and research challenges*, ACM TAAS 4(2), 2009. doi:10.1145/1516533.1516538.

## Unde căutați lucrări conexe

- Proceedings ALIFE și ECAL: https://direct.mit.edu/isal (acces gratuit). Căutați „traffic cellular automata”, „self-organizing traffic”.
- Google Scholar: porniți de la Nagel–Schreckenberg și Maerivoet–De Moor și folosiți „Cited by”.
- Pentru partea de control adaptiv: căutări ca „variable speed limit cellular automaton”, „adaptive traffic control cellular automata”.

## Documentație

- SUMO, documentația generală: https://sumo.dlr.de/docs/
- Importul din OpenStreetMap: https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- netconvert: https://sumo.dlr.de/docs/netconvert.html
- Definirea cererii (`<flow>`): https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html
- Detectoare E1 (induction loops): https://sumo.dlr.de/docs/Simulation/Output/Induction_Loops_Detectors_%28E1%29.html
- TraCI din Python: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html
- Overpass API și Overpass Turbo (pentru a vedea ce descărcați): https://overpass-turbo.eu
- NumPy, ghidul pentru începători: https://numpy.org/doc/stable/user/absolute_beginners.html

## Tutoriale practice

- SUMO, „Hello SUMO” (primul exemplu complet): https://sumo.dlr.de/docs/Tutorials/Hello_SUMO.html
- SUMO, tutorialul de import OSM: https://sumo.dlr.de/docs/Tutorials/Import_from_OpenStreetMap.html
- Golly sau orice vizualizator de automate celulare, pentru intuiție (opțional).

## Pe etape

Fiecare fișier din `milestones/` are o secțiune „Ce citiți acum”, cu lecturile potrivite momentului. Bibliografia de mai sus există și în format BibTeX, în `raport/latex/refs.bib`.

## Ce citiți întâi

1. Secțiunile despre NaSch, VDR și slow-to-start din Maerivoet și De Moor.
2. Tutorialul SUMO „Hello SUMO” și pagina despre importul OSM.
3. `docs/MAPEK.md` din acest kit.
