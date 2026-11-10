# Datele pentru P1

## Ce primiți în pachetul disciplinei

Folderul `p1_coridor/` din arhiva pusă la dispoziție de cadrul didactic. Copiați-l în `data/p1_coridor/`. Conține:

- coordonatele coridorului;
- extrasul OpenStreetMap pentru coridor;
- rețeaua SUMO corespunzătoare;
- profilul de flux pe oră (CSV) și o cerere sintetică cu vârf de dimineață, descrise în DATA.md din pachet.

Plus, din `common/`, zonele geografice ale zonei metropolitane și valorile unitare.

Începeți cu datele din pachet. Scripturile de mai jos vă ajută dacă vreți să refaceți rețeaua, să schimbați coridorul sau să înțelegeți cum s-a obținut extrasul.

## Scripturi

| Script | Ce face | Ieșire |
|---|---|---|
| `scripts/download_osm.py` | descarcă străzile din dreptunghiul `osm.bbox` prin Overpass API | `data/raw/coridor.osm` |
| `scripts/build_sumo_net.py` | construiește rețeaua SUMO cu `netconvert` | `data/sumo/coridor.net.xml` |
| `scripts/make_flows.py` | scrie cererea SUMO (`<flow>`) din profilul orar sau o cerere sintetică | `data/sumo/flows.rou.xml` |

Fluxul complet:

```bash
python scripts/download_osm.py --bbox <lon_min> <lat_min> <lon_max> <lat_max>   # sau completați osm.bbox
python scripts/build_sumo_net.py
netedit data/sumo/coridor.net.xml      # aflați ID-urile muchiilor de capăt -> config: sumo.from_edge / to_edge
python scripts/make_flows.py --profile data/p1_coridor/<profilul>.csv
```

Dreptunghiul din `config/default.yaml` este doar un exemplu din centrul Timișoarei; înlocuiți-l cu coordonatele coridorului din pachet.

## Licențe și citare

- OpenStreetMap: „© OpenStreetMap contributors”, licența ODbL (https://www.openstreetmap.org/copyright). Se citează în raport și în `data/DATA.md`.
- Rețeaua SUMO e generată cu instrumentele Eclipse SUMO din datele OSM; aceeași licență ODbL pentru date.
- Profilul de flux și cererea sintetică sunt **estimări de model**, nu numărători reale. Spuneți asta în raport.

## Ce notați în data/DATA.md

Pentru fiecare fișier: sursa, data obținerii, licența și ce prelucrări ați făcut (de exemplu, „rețea generată cu netconvert 1.27, opțiunile din scripts/build_sumo_net.py”).
