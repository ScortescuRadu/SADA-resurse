## P1: datele coridorului (din resursele SADA)

| Fișier | Sursă | Obținut la | Licență | Prelucrări |
|---|---|---|---|---|
| `p1_coridor/coridor.osm` | OpenStreetMap, prin Overpass API (`scripts/download_osm.py`, `osm.bbox` din config) | 2026-10-06 | ODbL, © OpenStreetMap contributors | niciuna |
| `p1_coridor/coordonate.json` | dreptunghiul `osm.bbox` și dimensiunile coridorului automatului din config | 2026-11-10 | – | – |
| `p1_coridor/profil_flux.csv` | **model**, nu numărătoare: aceeași formă ca `make_flows.py --synthetic` (bază 400 veh/h, vârf la 08:00) | 2026-11-10 | – | debit orar pe sens, 05:00–12:00 |

Profilul orar e o cerere sintetică cu vârf de dimineață, aleasă după capacitatea modelului, nu o măsurătoare din trafic. Scrieți asta în raport. Nivelurile lui (400–1635 veh/h) acoperă scenariile din config (600, 1200, 1800 veh/h).
