# Datele pentru P4

## Ce primiți în pachetul disciplinei

Folderul `p4_gtfs/`. Copiați-l în `data/p4_gtfs/` și verificați numele fișierelor în `config/default.yaml` (secțiunea `data`). Conține:

- feed-ul GTFS (sau instrucțiuni de descărcare și un extras deja curățat);
- liniile alese;
- un tabel cu încărcarea pe linie și pe fereastră de timp;
- capacitățile vehiculelor pe tip de mijloc de transport;
- lista zonelor cu acces slab la transport.

Din `common/`: zonele geografice ale zonei metropolitane (GeoJSON), utile pentru populație.

**Important:** încărcările provin dintr-un model de cerere, nu din validări reale de bilete. Raportul trebuie să precizeze acest lucru.

## Feed-ul GTFS

Fișa indică feed-ul din Mobility Database cu codul **mdb-2868**.

```bash
python scripts/download_gtfs.py
```

Scriptul încearcă adresele „latest” ale Mobility Database și dezarhivează în `data/raw/gtfs/`. Dacă nu merge, descărcați manual de pe https://mobilitydatabase.org/feeds/gtfs/mdb-2868 (butonul de descărcare din „Dataset History”) și dezarhivați în același loc.

Feed-ul se actualizează periodic. Notați data descărcării și perioada de valabilitate (le afișează scriptul) și folosiți același fișier în toate experimentele.

## Fișierele GTFS de care aveți nevoie

| Fișier | Ce conține | Pentru ce îl folosiți |
|---|---|---|
| `routes.txt` | liniile: `route_id`, `route_short_name`, `route_type` | alegerea liniilor, tipul de mijloc de transport |
| `trips.txt` | cursele: `trip_id`, `route_id`, `service_id`, `direction_id` | numărul de curse |
| `stop_times.txt` | orele fiecărei curse în fiecare stație | plecări, durate, intervale |
| `stops.txt` | stațiile, cu coordonate | acoperirea de 400 m |
| `calendar.txt`, `calendar_dates.txt` | în ce zile circulă fiecare serviciu | alegerea unei zile lucrătoare |

Tipul liniei (`route_type`): 0 tramvai, 3 autobuz, 11 troleibuz. Unele feed-uri folosesc tipurile extinse: 700 autobuz, 800 troleibuz, 900 tramvai. `scripts/inspect_gtfs.py` vă arată ce valori apar.

Specificația completă: https://gtfs.org/documentation/schedule/reference/

## Licențe și citare

- Feed-ul GTFS: licența e cea a operatorului, indicată pe pagina feed-ului din Mobility Database. Citați operatorul și Mobility Database ca sursă.
- Datele geografice din OpenStreetMap (dacă le folosiți): „© OpenStreetMap contributors”, licența ODbL.
- Încărcările, capacitățile și zonele: sursa e indicată în DATA.md din pachet.

## Ce notați în data/DATA.md

Fiecare fișier, cu sursa, data descărcării, perioada de valabilitate a feed-ului, licența și precizarea că încărcările sunt estimări de model.
