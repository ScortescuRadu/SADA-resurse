# Vizualizare

Fișa cere o vizualizare. Graficele din `results/figures/` arată rezultatul. Vizualizarea trebuie să arate *ce se întâmplă*: mașinile pe străzi, coada care se formează, strada care se închide și traficul care o ocolește, controllerul care decide. La prezentare, asta înțelege toată lumea din primele zece secunde.

Aici aveți două pagini care merg din prima și scripturile care le dau date:

| Fișier | Ce face |
|---|---|
| `sablon/index.html` | harta Timișoarei: străzile reale, cartierele, stațiile, spitalele și vehiculele care circulă pe ele. Pentru P2, P3, P4 |
| `sablon/coridor.html` | coridorul P1 văzut de sus, plus diagrama spațiu-timp |
| `exporta_harta.py` | scrie `sablon/date_harta.js` din `timisoara.sqlite`: nodurile, străzile, cartierele, stațiile |
| `exemplu_sim.py` | scrie `sablon/sim.js`: o simulare de jucărie (inundație pe Bega, mașini care își recalculează drumul) |
| `exemplu_coridor.py` | scrie `sablon/coridor_date.js`: un coridor cu un incident, pentru `coridor.html` |

Fișierele `.js` din `sablon/` sunt deja generate, ca paginile să meargă imediat.

## Pornire

Folderul ajunge în repo, la `vizualizare/`, odată cu resursele temei (`python instaleaza.py P3 ...`). Dacă vreți doar vizualizarea:

```bash
python instaleaza.py vizualizare ../repo_nostru
```

Apoi, din repo:

```bash
python -m http.server 8000 --directory vizualizare/sablon
```

Deschideți http://localhost:8000 pentru hartă sau http://localhost:8000/coridor.html pentru P1. Merge și cu dublu-clic pe `index.html`, fără server, pentru că datele vin ca `<script>`, nu prin `fetch`.

Lucrați pe o copie:

```bash
cp -r vizualizare/sablon vizualizare/pagina
```

și scrieți exporturile acolo (`python vizualizare/exemplu_sim.py --out vizualizare/pagina/sim.js`). La o nouă instalare, `sablon/` se actualizează, iar `pagina/` rămâne cum ați lăsat-o.

## Cum legați simularea de pagină

Sunt două variante. Pentru proiect, prima e aproape întotdeauna cea bună.

**1. Reluare (recomandat).** Simularea rulează în Python, ca de obicei. În timp ce rulează, scrieți ce s-a întâmplat într-un fișier `.js`. Pagina doar redă fișierul. Avantaje: e exact simularea din raport, nu o copie; puteți da timpul înainte și înapoi; puteți face câte un fișier pe scenariu și le comparați (`index.html?sim=sim_fix.js` și `index.html?sim=sim_adaptiv.js`, în două taburi).

**2. Model portat în JS.** Rescrieți modelul în pagină și rulează live, cu butoane care schimbă parametri. Arată bine la prezentare, dar aveți de întreținut două implementări. Dacă alegeți asta, comparați numerele: rulați același scenariu, cu același seed, în Python și în pagină. Metrica principală trebuie să iasă la fel, sau măcar foarte aproape dacă generatoarele aleatoare diferă. Scrieți comparația în raport.

### Formatul pentru hartă (`sim.js`)

```js
window.SIM = {
  descriere: "S2, controller adaptiv, seed 3",
  durata_s: 3600,
  vehicule: [
    { id: "m17", stare: "redirecționat", puncte: [[0, "115"], [14.2, "117"], [31.0, "2034"]] },
    { id: "bus_13_07", culoare: "#5ec8e5", puncte: [[0, 21.181, 45.764], [60, 21.192, 45.766]] }
  ],
  evenimente: [
    { t_s: 1200, text: "faza 1: 43 de muchii închise", inchise: [["115", "117"], ["117", "115"]] },
    { t_s: 2700, text: "controllerul redeschide podul", redeschise: [["115", "117"]] }
  ]
}
```

- Un punct e `[timp_s, nod]` (id-ul din `retea.graphml`, ca șir) sau `[timp_s, lon, lat]`. Pagina interpolează între puncte după timp, deci viteza se vede singură.
- `stare` poate fi `"redirecționat"` (violet) sau `"blocat"` (rămâne pe hartă, roșu, după ultimul punct). `culoare` le suprascrie pe toate.
- `evenimente` apar în jurnal la momentul lor, iar muchiile din `inchise` se desenează cu roșu.

Cel mai simplu e să construiți lista în Python și să o scrieți la final:

```python
import json
vehicule = []          # în simulare: vehicule.append({"id": ..., "puncte": [[t, nod], ...]})
evenimente = []        # evenimente.append({"t_s": t, "text": "...", "inchise": [[u, v], ...]})
with open("vizualizare/sim_adaptiv.js", "w", encoding="utf-8") as f:
    f.write("window.SIM = " + json.dumps({"descriere": "...", "durata_s": T,
            "vehicule": vehicule, "evenimente": evenimente}, ensure_ascii=False) + ";")
```

`exemplu_sim.py` face exact asta, de la cap la coadă, în vreo 100 de rânduri. Citiți-l înainte să scrieți varianta voastră.

### Formatul pentru coridor (`coridor_date.js`)

Matricea benzi × celule din `Corridor`, câte un șir pe pas: `.` pentru celulă goală, cifra pentru viteză. Detaliile sunt la începutul lui `exemplu_coridor.py`.

## Pe teme

### P1. Coridorul

`coridor.html` are deja trei lucruri: drumul de sus, cu vehiculele colorate după viteză; diagrama spațiu-timp pe o bandă; densitatea și viteza pe tronsoane la pasul curent.

- **Diagrama spațiu-timp e figura cea mai importantă.** Undele de oprire apar ca dungi roșii care merg înapoi, spre intrare. Coada de la incident e un triunghi care crește, apoi se închide. Timpul de recuperare se vede direct: e distanța pe verticală de la sfârșitul incidentului până dispare pata. Puneți varianta fixă și pe cea adaptivă una lângă alta, cu aceeași scară.
- Exportați din `Corridor` la fiecare pas (`"".join(...)`, ca în exemplu). La 3 benzi × 400 de celule × 3600 de pași ies ~4 MB, încă bine. Peste 10 MB, exportați doar din 2 în 2 pași.
- Puneți în `evenimente` deciziile controllerului: `{"pas": 812, "text": "tronson 6: nasch -> vdr"}`. Ca să vedeți și pe drum regula curentă, adăugați în `drum()` o bandă colorată sub fiecare tronson.
- Exemplul nu are încetinire aleatoare și nici schimbare de bandă. Cu modelul vostru, coada trebuie să se întindă și pe benzile vecine.

### P2. Portofoliul

Aici nu se mișcă mașini, se mișcă alegerile algoritmului. Intervențiile au coordonate în `timisoara.sqlite`, tabelul `interventii` (`lon`, `lat`, `linie_wkt` pentru coridoare).

- Exportați câte un rând pe generație: cel mai bun individ (șirul de biți) și fitness-ul, plus frontul Pareto la final. În pagină, intervențiile alese se aprind, celelalte rămân gri, iar un grafic mic arată convergența. Cu bara de timp, publicul vede cum algoritmul renunță la unele intervenții și adaugă altele.
- La schimbarea de buget (scenariul cu `changes_*.json`), puneți un eveniment: e momentul în care se vede dacă soluția se reface din populația veche sau o ia de la zero.
- Desenarea unui strat nou, în `deseneaza()`, după străzi:

```js
for (const iv of window.P2.interventii) {                 // exportate din tabelul interventii
  const [x, y] = proj([iv.lon, iv.lat]), ales = bitiCurenti[iv.k] === "1";
  cx.fillStyle = ales ? "#7ee787" : "#ffffff30";
  cx.beginPath(); cx.arc(X(x), Y(y), ales ? 7 : 4, 0, 7); cx.fill();
}
```

### P3. Rețeaua

Formatul `sim.js` e făcut pentru tema asta. `exemplu_sim.py` e aproape scheletul vostru: înlocuiți drumul minim cu rutele voastre (principală, rezervă, recalculată) și închiderea cu scenariile din `scenarii_defect.json`.

- Colorați vehiculele după nivelul de recuperare care le-a salvat: rezervă precalculată, recalculare locală, recalculare globală. Asta arată direct ierarhia din fișă. Puneți nivelul în `stare` sau în `culoare`.
- Perechile fără drum: desenați originea cu un cerc roșu cât timp e deconectată. Perechile prioritare spre spitale merită culoarea lor.
- La inundație, fazele vin ca evenimente separate, ca să se vadă apa care crește.
- **Bucla Langton** nu are nevoie de hartă. Un canvas și `ImageData`, câte un pixel (sau câte un pătrat de 3×3) pe celulă:

```js
const g = cv.getContext("2d"), img = g.createImageData(W, H);
const PAL = [[0,0,0],[0,0,255],[255,0,0],[0,255,0],[255,255,0],[255,0,255],[255,255,255],[0,255,255]];
function arata(grid) {                                    // grid: Uint8Array W*H, stări 0..7
  for (let i = 0; i < grid.length; i++) img.data.set([...PAL[grid[i]], 255], 4 * i);
  g.putImageData(img, 0, 0);
}
```

Paleta e cea din Golly, ca figurile să semene cu ce știe lumea. Dacă exportați stările din Python (`grid.tobytes()`, codificat base64), pagina doar redă. Altfel, portați `TableCA.step`: e un tabel de căutare, iese scurt.

### P4. Transportul

Vehiculele merg pe trasee GTFS, nu pe graful nostru, deci folosiți punctele `[t, lon, lat]`. Din `stop_times` ies direct, câte o cursă pe vehicul:

```python
from sada.p4.gtfs_io import load_feed, active_service_ids, time_to_seconds
feed = load_feed("data/raw/gtfs")
sids = active_service_ids(feed, "2026-10-14")
trips = feed["trips"][feed["trips"].service_id.isin(sids) & feed["trips"].route_id.isin(rute)]
st = (feed["stop_times"].merge(trips[["trip_id", "route_id"]], on="trip_id")
      .merge(feed["stops"][["stop_id", "stop_lon", "stop_lat"]], on="stop_id"))
st["t"] = time_to_seconds(st.arrival_time) - 7 * 3600              # secunde de la 07:00
st = st[st.t.between(-1800, 7200)].sort_values(["trip_id", "stop_sequence"])
vehicule = [{"id": trip, "puncte": d[["t", "stop_lon", "stop_lat"]].astype(float).round(5).values.tolist()}
            for trip, d in st.groupby("trip_id")]
```

- Asta e orarul din GTFS. Pentru scenariile voastre, generați cursele din numărul de curse pe fereastră ales de controller: plecările la intervale egale, iar timpii dintre stații îi luați dintr-o cursă GTFS a aceleiași linii.
- **Culoarea = gradul de încărcare** al cursei (pasageri / capacitate): verde sub 0,7, galben până la 1, roșu peste. Calculați-l în Python și puneți-l în `culoare`. Când controllerul mută curse de pe o linie pe alta, se vede imediat cum linia aglomerată se înverzește.
- Între stații, vehiculul merge în linie dreaptă. Ca să urmeze străzile, folosiți `shapes.txt` (`shape_id` din `trips`) și puneți punctele formei între stații, cu timpii interpolați după `shape_dist_traveled`. E opțional; la zoom mic nu se observă.
- Cartierele cu acces slab sunt deja colorate pe hartă. Dacă metrica de acoperire se schimbă între scenarii, refaceți `acces_slab` în export și arătați diferența.

## Capcane

- **`fetch()` nu merge de pe `file://`.** De aceea datele sunt `window.X = {...}` în fișiere `.js`. Cu `http.server` merge orice.
- **Browserul ține minte versiunea veche.** După ce rescrieți `sim.js`, reîncărcați cu Cmd+Shift+R (Ctrl+F5) sau adăugați `?v=2` la adresă.
- **Nu calculați la fiecare cadru ce se poate calcula o dată.** Pagina desenează de 60 de ori pe secundă. `getComputedStyle`, căutări prin toate muchiile, `JSON.parse` în buclă fac animația sacadată. Precalculați, ca în diagrama spațiu-timp.
- **Canvasul neclar pe ecrane retina:** dimensiunea internă trebuie înmulțită cu `devicePixelRatio`. Șabloanele fac deja asta, în `fit()` și în `scena()`.
- **Harta turtită:** longitudinea se înmulțește cu cos(45,75°). Vedeți `proj` în `index.html`.
- **Fișiere prea mari.** Peste 30–40 MB, browserul se încurcă. Rotunjiți coordonatele la 5 zecimale (~1 m) și timpii la o zecime de secundă, sau exportați mai rar.
- **Vizualizarea nu e o dovadă.** Ce arată pagina trebuie să se potrivească cu numerele din raport. Dacă în tabel recuperarea durează 6 minute și pe hartă coada dispare în 2, una dintre ele e greșită.
