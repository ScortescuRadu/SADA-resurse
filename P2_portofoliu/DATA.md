# Proveniența datelor (de copiat în data/DATA.md)

| Fișier | Sursă | Obținut la | Licență | Prelucrări |
|---|---|---|---|---|
| `raw/timisoara/populatie_grila.csv` | construit din clădirile OpenStreetMap (același fișier ca în resursele P4) | 2026-10-14 | ODbL, © OpenStreetMap contributors | **model**: suprafața desfășurată a clădirilor rezidențiale / 30 m² pe locuitor, grilă de 200 m (Stereo 70); ~315 000 de locuitori |
| `raw/timisoara/statii_linii.csv` | derivat din GTFS STPT/SMTT (Mobility Database mdb-2868, valabil 2026-10-01 – 2026-12-31) | 2026-10-14 | licența operatorului | stațiile liniilor urbane și intervalul lor în vârful de dimineață (miercuri 2026-10-14) |
| `raw/timisoara/zone.geojson`, `zone_acces_slab.geojson` | derivate din OSM `place=*` | 2026-10-14 | ODbL | 34 de cartiere; cele 6 cu cea mai mică acoperire cu transport public |
| `p2_portofoliu/tm_A_40.json` | `scripts/build_portfolio.py`, seed 22 | 2026-10-14 | derivat (ODbL, GTFS) | 40 de intervenții urbane cu locație reală (vedeți mai jos), costuri și beneficii din **modelul de evaluare**; 54 de perechi cu zone de influență suprapuse (interacțiuni); bugetul = 35% din costul total (6,1 mil. EUR) |
| `p2_portofoliu/tm_A_20.json` | idem | 2026-10-14 | idem | 20 dintre ele (jumătate din fiecare tip); bugetul = 40% din costul lor |
| `p2_portofoliu/changes_*.json` | idem | 2026-10-14 | – | scenariile de schimbare: −30% buget (g 100), aviz refuzat pentru intervenția cea mai valoroasă din optimul stării (g 200), ponderi 50/50 (g 300); varianta `_revenire`: −30%, revine, −30% |

## Cum s-au ales intervențiile (ramura A)

- **semaforizare adaptivă** (6) și **reorganizarea intersecției** (4): în jurul stațiilor STPT prin care trec cele mai multe linii, la cel puțin 700 m una de alta;
- **trecere semaforizată** (7) și **zonă 30** (4): la stațiile care poartă numele unei școli, licee, colegii sau facultăți;
- **stație accesibilă** (6): câte o stație în cele mai populate cartiere;
- **bandă de biciclete** (7): între centrele de populație ale unor cartiere vecine;
- **microbuz de cartier** (4): în cartierele cu acces slab la transport public;
- **P+R** (2): la capetele liniilor cele mai depărtate de centru.

## Modelul de evaluare (ipoteze, nu măsurători)

- cost = costul unitar al tipului × mărime × factor lognormal (σ = 0,25); costurile unitare sunt în `config/default.yaml` (`portfolio.types`);
- beneficiu = populația din zona de influență × efectul tipului [ore-persoană echivalente pe an, timp + siguranță], / 1000, × factor lognormal (σ = 0,30);
- echitate = aceeași sumă, numai pentru populația fără acces bun la transport (nicio stație cu interval ≤ 20 min la 400 m), dublată în cartierele cu acces slab;
- interacțiuni: r_ij = 0,6 × min(b_i · P_ij / P_i, b_j · P_ij / P_j), unde P_ij e populația din zona de influență comună.

**Beneficiile și echitatea sunt estimări de model, nu valori măsurate.** Pachetul `p2_portofoliu/` al disciplinei nu e încă disponibil. Dacă îl primiți, puneți căile lui în `config/default.yaml` (secțiunea `scenarios`); restul codului lucrează cu clasa `Problem`.
