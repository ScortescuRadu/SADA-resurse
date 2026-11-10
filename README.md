# Resurse suplimentare pentru proiectele SADA

Aici găsiți tot ce vă trebuie ca să porniți proiectul:
- **kiturile de pornire** ale celor patru teme, în `kituri/`: codul de bază, ghidul pas cu pas, testele și scriptul care vă instalează mediul Python;
- **datele**: kiturile presupun un pachet de date al disciplinei (`p1_coridor/`, `p2_portofoliu/`, `p3_retea/`, `p4_gtfs/`) care nu e încă gata. Ca să nu stați după el, am construit date echivalente pe Timișoara, din surse publice: OpenStreetMap și orarul STPT în format GTFS;
- scripturile care refac datele;
- câteva unelte care v-ar fi luat mult timp și nu se notează;
- un script care le pune în repo-ul vostru.

Nu găsiți aici controllere, algoritmi genetici, experimente sau rezultate. Partea aia e proiectul vostru și pe ea se face evaluarea.

## Ce e în folder

```
SADA_resurse_studenti/
├── README.md               fișierul ăsta
├── instaleaza.py           pune resursele în repo-ul echipei
├── verifica.py             verifică dacă totul e la locul lui și se încarcă
├── descarca.py             reia sursele originale de pe internet (opțional)
├── MANIFEST.json           sumele de control ale fișierelor (le folosește verifica.py)
├── kituri/                 kiturile de pornire, câte unul pe temă (de aici porniți repo-ul echipei)
├── comun/                  pentru toate echipele
│   ├── README.md           statistica pe perechi + greșelile pe care le-am întâlnit
│   ├── statistica_pereche.py
│   ├── timisoara/          toate datele despre oraș într-o bază SQLite, cu un modul de citire
│   └── vizualizare/        hartă cu mașini pe străzile reale, coridorul P1, ghid pe fiecare temă
├── P1_trafic/              datele coridorului, referința SUMO pe coridorul drept
├── P2_portofoliu/          portofoliul de intervenții, optimul exact, frontul Pareto exact
├── P3_retea/               rețeaua rutieră, scenariile de defect, spitalele, regulile Golly
└── P4_transport/           feed-ul GTFS, încărcările, capacitățile, populația, cartierele, întoarcerea la capăt
```

Fiecare folder de temă are trei fișiere de citit:
- `README.md`: ce primiți și ce aveți de făcut;
- `DATA.md`: de unde vin datele, de copiat în raport;
- `config_de_adaugat.yaml`: ce intră în config.

## Pașii, pe scurt

Exemplele sunt pentru P3; înlocuiți cu tema voastră (P1, P2, P3 sau P4). Comenzile sunt pentru Linux, macOS sau WSL; pe Windows, în PowerShell, scrieți `python` în loc de `python3`, iar căile cu `\`.

**1. Faceți repo-ul echipei din kitul temei.** Copiați kitul lângă folderul de resurse, nu în el, și faceți din el un repo Git:

```bash
cd proiecte
git clone https://github.com/ScortescuRadu/SADA-resurse SADA_resurse_studenti
cp -r SADA_resurse_studenti/kituri/P3_toleranta_retea_mobilitate repo_nostru
cd repo_nostru
git init && git add -A && git commit -m "Kitul de pornire P3"
```

Pe Windows, în PowerShell: `Copy-Item -Recurse SADA_resurse_studenti\kituri\P3_toleranta_retea_mobilitate repo_nostru`.

| Tema | Kitul |
|---|---|
| P1 | `kituri/P1_trafic_automate_celulare` |
| P2 | `kituri/P2_algoritm_genetic_portofoliu` |
| P3 | `kituri/P3_toleranta_retea_mobilitate` |
| P4 | `kituri/P4_frecventa_transport_public` |

La final aveți:

```
proiecte/
├── SADA_resurse_studenti/
└── repo_nostru/          (kitul vostru: config/, src/, scripts/, setup/ ...)
```

**2. Instalați și activați mediul din kit.** Scripturile din resurse folosesc pachetele din kit (pyyaml, pandas, networkx...). E nevoie de Python 3.10 sau mai nou.

```bash
cd repo_nostru
bash setup/setup.sh                # Windows: powershell -ExecutionPolicy Bypass -File setup\setup.ps1
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
python examples/toy_mapek.py       # trebuie să ruleze fără erori
cd ../SADA_resurse_studenti
```

Instalarea durează câteva minute și se face o singură dată. După aceea, în fiecare terminal nou, doar activați mediul. Pe macOS, `python3` din sistem e uneori 3.9; atunci rulați `PYTHON=python3.12 bash setup/setup.sh` (sau ce versiune ≥ 3.10 aveți).

**3. Vedeți întâi ce s-ar schimba, fără să scrie nimic:**

```bash
python instaleaza.py P3 ../repo_nostru --simulare
```

**4. Instalați:**

```bash
python instaleaza.py P3 ../repo_nostru
```

Scriptul copiază datele și scripturile la aceleași căi ca în kit și adaugă secțiunile necesare în `config/default.yaml`. La sfârșit rulează verificarea; trebuie să vedeți `Totul e în regulă.`

**5. Faceți commit.** Uitați-vă întâi cu `git status` și `git diff config/default.yaml` la ce s-a schimbat.

## Ce face instaleaza.py și ce nu face

Face:
- verifică întâi că repo-ul e al temei alese. Dacă dați P3 pe un repo P2, se oprește;
- copiază fișierele temei, plus `statistica_pereche.py` în `src/sada/`, baza cu Timișoara în `data/timisoara/` și șabloanele de vizualizare în `vizualizare/`;
- adaugă în `config/default.yaml` doar cheile din `config_de_adaugat.yaml`. Restul config-ului și comentariile voastre rămân;
- adaugă la sfârșitul lui `data/DATA.md` proveniența datelor.

Nu face:
- nu șterge nimic. Dacă un fișier există deja și e diferit (de exemplu ați modificat `problem.py` la P2), vechiul rămâne alături cu sufixul `.inainte_de_resurse`. La fel pentru `config/default.yaml`;
- nu modifică fișierele care sunt deja identice. Îl puteți rula de câte ori vreți.

Opțiuni:
- `--fara-config`: dacă vreți să adăugați singuri secțiunile în config;
- `--fara-verificare`: sare peste verificarea de la final.

## Doar baza de date cu Timișoara

Orice echipă, inclusiv P1, poate lua doar datele despre oraș:

```bash
python instaleaza.py timisoara ../repo_nostru
```

Ce e în ea și cum o folosiți: `comun/timisoara/README.md`.

## Vizualizarea

Două pagini care merg din prima: harta Timișoarei, cu vehiculele care circulă pe străzile reale, și coridorul P1, cu diagrama spațiu-timp. Vin cu instalarea temei. Doar ele:

```bash
python instaleaza.py vizualizare ../repo_nostru
python -m http.server 8000 --directory ../repo_nostru/vizualizare/sablon
```

Deschideți http://localhost:8000. Cum le legați de simularea voastră și ce merită arătat pe fiecare temă: `comun/vizualizare/README.md`.

## Verificarea

```bash
python verifica.py                              # sunt întregi fișierele din folderul de resurse?
python verifica.py P3 ../repo_nostru       # e totul la locul lui în repo și se încarcă?
```

Fiecare linie e `[ok]`, `[atenție]` (merge, dar e ceva de făcut, de exemplu optimele necalculate) sau `[PROBLEMĂ]`, cu comanda care o rezolvă dedesubt.

## Reguli

- **Datele sunt construite de noi.** Populația, beneficiile și încărcările sunt estimări de model, nu măsurători. Scrieți asta în raport și în `data/DATA.md`.
- **Pachetul oficial.** Dacă îl primiți înainte de predare, îl puteți folosi pe acela; spuneți în raport pe ce date ați rulat.
- **Modificările.** Scripturile de aici le puteți modifica. Dacă schimbați un parametru al datelor (de exemplu calibrarea cererii la P4), spuneți ce și de ce.
- **Declarația privind instrumentele.** Treceți acolo și folderul ăsta, cu ce ați folosit din el.

## Dacă ceva nu merge

| Mesaj | Ce faceți |
|---|---|
| `ModuleNotFoundError: No module named 'yaml'` (sau `pandas`, `networkx`) | nu ați activat mediul din kit, pasul 2 |
| `E nevoie de Python 3.10 sau mai nou` la `setup.sh` | instalați Python 3.10+ și rulați `PYTHON=python3.12 bash setup/setup.sh` |
| `No such file or directory: setup/setup.sh` | nu sunteți în folderul kitului; pasul 1 |
| `nu pare un repo de proiect SADA` | calea către repo e greșită; trebuie să fie folderul care conține `config/` |
| `Repo-ul nu are src/sada/p3/; pare să fie P2` | ați dat altă temă decât a voastră |
| `Nu am modificat config/default.yaml` | config-ul vostru are o formă pe care scriptul n-o recunoaște sigur; adăugați secțiunile de mână din `config_de_adaugat.yaml` și rulați `verifica.py` |
| `[PROBLEMĂ] ... diferă de datele din resurse` | dacă le-ați refăcut voi cu `build_*`, e în regulă; altfel reinstalați |
