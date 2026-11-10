# Datele pentru P3

## Ce primiți în pachetul disciplinei

Folderul `p3_retea/`. Copiați-l în `data/p3_retea/` și puneți numele fișierelor în `config/default.yaml` (secțiunea `data`). Conține:

- graful extras din rețeaua rutieră, în format GraphML;
- populația pe noduri;
- un fișier de sinteză cu trei scenarii de defect în grup (coridor de inundație, traversări de râu, coridor central);
- lista muchiilor cu cea mai mare importanță.

Deschideți întâi fișierul de sinteză și vedeți cum sunt identificate muchiile (perechi de noduri, ID-uri OSM etc.); de asta depinde cum scrieți `group_failure`.

## Rețeaua din OpenStreetMap (opțional)

```bash
python scripts/download_graph.py --lat <lat> --lon <lon> --dist 1500
```

Descarcă rețeaua pentru mașini cu OSMnx, unește intersecțiile apropiate (toleranța implicită 15 m), păstrează componenta tare conexă cea mai mare, adaugă viteze și timpi de parcurs și salvează în `data/raw/retea_osm.graphml`. Valorile din config sunt doar un exemplu din centrul Timișoarei. Scriptul vă spune dacă numărul de noduri e în intervalul 500–3000 cerut.

Rețeaua descărcată nu are populație pe noduri. Pentru experimente folosiți graful din pachet; varianta descărcată e utilă ca să înțelegeți proveniența datelor sau pentru teste.

## Regulile pentru bucla Langton și bucla Byl

Ambele vin cu programul **Golly** (gratuit, https://golly.sourceforge.io):

1. Instalați Golly.
2. În folderul `Rules` al instalării găsiți fișierele de reguli (pentru bucla Langton și bucla Byl). Numele exacte pot diferi ușor de la o versiune la alta; căutați „Langton” și „Byl”.
3. Configurațiile inițiale sunt în `Patterns/Loops/`, în format `.rle` (tot acolo găsiți și variantele mai noi: SDSR, Evoloop). Deschideți-le întâi în Golly ca să vedeți cum arată.
4. Copiați fișierele în `data/ca/` și rulați:

```bash
python scripts/run_ca.py --rule data/ca/Langtons-Loops.rule --pattern data/ca/<model>.rle --size 128 --steps 1200
```

Rulați același model și în Golly: dacă instantaneele coincid, citirea regulii și a modelului e corectă. Dacă fișierul de reguli are și secțiuni pe care cititorul din kit nu le cunoaște (de exemplu `@TREE` fără `@TABLE`), deschideți-l într-un editor de text: kitul citește doar secțiunea `@TABLE`. Bucla Langton are nevoie de spațiu: dacă replicile se lovesc de margine, măriți `--size`.

## Licențe și citare

- OpenStreetMap: „© OpenStreetMap contributors”, licența ODbL.
- Regulile și modelele din Golly: citați articolul original (Langton, 1984, sau Byl, 1989) și menționați Golly ca sursă a fișierelor.
- Populația pe noduri: sursa e indicată în DATA.md din pachet.

## Ce notați în data/DATA.md

Fiecare fișier, cu sursa, data, licența și prelucrările (de exemplu „componenta tare conexă cea mai mare; intersecții unite la 15 m”).
