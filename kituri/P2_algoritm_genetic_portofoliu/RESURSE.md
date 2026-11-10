# Resurse pentru P2

Verificați datele bibliografice în baza de date a bibliotecii înainte de a le prelua în raport.

## Articole și cărți de pornire

- J. Branke, *Evolutionary Optimization in Dynamic Environments*, Kluwer, 2002. Cartea de referință pentru algoritmi evolutivi în medii care se schimbă: detecție, memorie, diversitate.
- K. Deb, A. Pratap, S. Agarwal, T. Meyarivan, *A fast and elitist multiobjective genetic algorithm: NSGA-II*, IEEE Trans. Evolutionary Computation 6(2), 2002. doi:10.1109/4235.996017.
- D. E. Goldberg, *Genetic Algorithms in Search, Optimization and Machine Learning*, Addison-Wesley, 1989. Operatorii de bază.
- H. G. Cobb, *An investigation into the use of hypermutation as an adaptive operator in genetic algorithms having continuous, time-dependent nonstationary environments*, NRL Memorandum Report 6760, 1990. Originea hipermutației.
- J. J. Grefenstette, *Genetic algorithms for changing environments*, Parallel Problem Solving from Nature 2, 1992. Imigranții aleatori.
- T. T. Nguyen, S. Yang, J. Branke, *Evolutionary dynamic optimization: A survey of the state of the art*, Swarm and Evolutionary Computation 6, 2012. Trecere în revistă, bună pentru secțiunea de lucrări conexe.
- A. Vargha, H. D. Delaney, *A critique and improvement of the CL common language effect size statistics*, J. Educational and Behavioral Statistics 25(2), 2000. Măsura A12 folosită în `sada.stats`.

## Sisteme autoadaptive

- J. O. Kephart, D. M. Chess, *The vision of autonomic computing*, IEEE Computer 36(1), 2003. doi:10.1109/MC.2003.1160055.
- M. Salehie, L. Tahvildari, *Self-adaptive software: landscape and research challenges*, ACM TAAS 4(2), 2009. doi:10.1145/1516533.1516538.

## Unde căutați lucrări conexe

- Proceedings GECCO în ACM Digital Library (dl.acm.org). Căutări utile: „dynamic knapsack evolutionary”, „change detection dynamic optimization”, „hypermutation”, „random immigrants”.
- Google Scholar, pornind de la Branke (2002) și Nguyen et al. (2012), cu „Cited by”.
- Benchmark-uri pentru probleme dinamice: „moving peaks benchmark” (Branke) și „dynamic knapsack problem”.

## Biblioteci

- DEAP: https://deap.readthedocs.io (tutorialul „One Max Problem” e un punct de pornire bun pentru vectori binari)
- pymoo: https://pymoo.org (NSGA-II, probleme binare, indicatorul de hipervolum)
- NumPy, ghid pentru începători: https://numpy.org/doc/stable/user/absolute_beginners.html

## Tutoriale practice

- DEAP, „One Max” (algoritm genetic pe vectori binari): https://deap.readthedocs.io/en/master/examples/ga_onemax.html
- pymoo, „Getting Started” (NSGA-II, problema cu constrângeri): https://pymoo.org/getting_started/index.html

## Pe etape

Fiecare fișier din `milestones/` are o secțiune „Ce citiți acum”, cu lecturile potrivite momentului. Bibliografia de mai sus există și în format BibTeX, în `raport/latex/refs.bib`.

## Ce citiți întâi

1. Capitolele introductive din Branke (2002) sau trecerea în revistă Nguyen et al. (2012).
2. Tutorialul DEAP „One Max”, ca să vedeți operatorii în cod.
3. `docs/MAPEK.md` și `docs/STATISTICA.md` din acest kit.
