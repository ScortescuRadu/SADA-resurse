# Resurse pentru P4

Verificați datele bibliografice în baza de date a bibliotecii înainte de a le prelua în raport.

## Cărți și articole de pornire

- A. Ceder, *Public Transit Planning and Operation: Modeling, Practice and Behavior*, Elsevier, 2007. Capitolele despre determinarea frecvenței și a intervalelor (metodele bazate pe încărcarea maximă) sunt direct utile pentru regula simplă și pentru fitness.
- V. Guihaire, J.-K. Hao, *Transit network design and scheduling: a global review*, Transportation Research Part A 42(10), 2008. doi:10.1016/j.tra.2008.03.011. Trecere în revistă; bună pentru lucrările conexe.
- K. Deb et al., *A fast and elitist multiobjective genetic algorithm: NSGA-II*, IEEE Trans. Evolutionary Computation 6(2), 2002. doi:10.1109/4235.996017. Util dacă tratați așteptarea și supraaglomerarea ca obiective separate.

## Sisteme autoadaptive

- J. O. Kephart, D. M. Chess, *The vision of autonomic computing*, IEEE Computer 36(1), 2003. doi:10.1109/MC.2003.1160055.
- M. Salehie, L. Tahvildari, *Self-adaptive software: landscape and research challenges*, ACM TAAS 4(2), 2009. doi:10.1145/1516533.1516538.

## Unde căutați lucrări conexe

- GECCO (ACM Digital Library): „transit frequency setting genetic algorithm”, „bus frequency optimization evolutionary”.
- Google Scholar: „transit frequency setting”, „dynamic headway control”, „real-time bus frequency adjustment”, „transit network frequency setting problem”.
- Pentru acoperire și accesibilitate: „transit accessibility 400 m catchment”.

## Date și specificații

- Specificația GTFS Schedule: https://gtfs.org/documentation/schedule/reference/
- Mobility Database (catalogul de feed-uri): https://mobilitydatabase.org
- Validatorul GTFS (verifică dacă feed-ul are erori): https://gtfs-validator.mobilitydata.org
- EPSG:3844 (Stereo 70): https://epsg.io/3844

## Biblioteci

- pandas: https://pandas.pydata.org/docs/
- gtfs-kit (opțional): https://github.com/mrcagney/gtfs_kit
- pyproj: https://pyproj4.github.io/pyproj/
- scipy.spatial.cKDTree: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html
- DEAP: https://deap.readthedocs.io

## Tutoriale practice

- Referința GTFS Schedule, cu exemple: https://gtfs.org/documentation/schedule/reference/
- pandas, „10 minutes to pandas”: https://pandas.pydata.org/docs/user_guide/10min.html
- pyproj, transformări de coordonate: https://pyproj4.github.io/pyproj/stable/examples.html

## Pe etape

Fiecare fișier din `milestones/` are o secțiune „Ce citiți acum”, cu lecturile potrivite momentului. Bibliografia de mai sus există și în format BibTeX, în `raport/latex/refs.bib`.

## Ce citiți întâi

1. Pagina de referință GTFS pentru `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`.
2. Capitolul despre frecvențe din Ceder (2007).
3. `docs/MAPEK.md` și `docs/STATISTICA.md` din acest kit.
