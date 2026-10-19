# Comun

Trei lucruri folositoare oricărei teme:
- `statistica_pereche.py` (mai jos);
- `timisoara/`: toate datele despre oraș într-o bază SQLite, cu instrucțiunile în `timisoara/README.md`;
- `vizualizare/`: o hartă cu vehicule pe străzile reale și coridorul P1, cu ghidul în `vizualizare/README.md`.

## statistica_pereche.py

Îl puneți în `src/sada/`, lângă `stats.py`.

`report_numbers.py` din kit folosește Mann–Whitney: tratează variantele ca două grupuri independente. Dar dacă `run_one` folosește seed-ul la fel în toate variantele, rulările sunt pereche: același seed înseamnă aceeași cerere, aceleași defecte sau aceeași populație inițială. Atunci testul potrivit e Wilcoxon cu semn pe diferențe. Are mult mai multă putere pentru că scoate variația dintre seed-uri.

```python
import pandas as pd
from sada.statistica_pereche import paired_table, to_markdown

df = pd.read_csv("results/results.csv")
t = paired_table(df, scenarios=df.scenario.unique(),
                 comparisons=[("adaptiv", "fix")], metrics=["travel_time_mean"])
open("results/tables/comparisons_paired.md", "w").write(to_markdown(t))
```

Ce vă dă pe fiecare rând: mediile, diferența medie cu interval de încredere bootstrap, p Wilcoxon, p corectat Holm și A12.

Două lucruri de verificat înainte:

1. Chiar sunt pereche? Rulați aceeași variantă de două ori cu același seed și comparați. Dacă iese altceva, undeva se folosește un generator aleator fără seed (de exemplu `np.random.random()` în loc de `rng`).
2. Corecția Holm se face pe tot tabelul, nu pe câte o metrică. Cu 60 de teste, câteva ies „semnificative” din întâmplare.

## Greșeli pe care le-am văzut

Le-am întâlnit construind datele de aici, nu sunt ipotetice.

**Comparați la același număr de evaluări, nu de generații sau de pași.** Dacă o variantă face evaluări în plus (santinele, rulări de prognoză), ele se numără.

**Scenarii deterministe rulate cu 20 de seed-uri.** Un defect în grup fără nicio componentă aleatoare dă de 20 de ori același rezultat. Nu calculați p pe asta; raportați valoarea, iar diferența dintre variante e exactă. `paired_table` le marchează singur.

**Controllerul care vede viitorul.** Ordinea corectă într-un pas e: lumea evoluează cu decizia veche, apoi controllerul măsoară și decide pentru pasul următor. Dacă îl lăsați să măsoare înainte să servească pasul (cum face `demo_prototip.py` din kitul P4), are informații pe care nu le-ar avea în realitate.

**Optimul „exact” care nu e exact.** `scipy.optimize.milp` (HiGHS) se oprește implicit la o diferență relativă de 10⁻⁴ față de optim. Pentru un reper, puneți `options={"mip_rel_gap": 0}`.

**Rezultate care nu se reproduc.** Ordinea elementelor dintr-un `set` de șiruri se schimbă de la o rulare la alta (randomizarea hash-urilor în Python). Dacă alegeți „primele k” dintr-un set, sortați întâi. Ca verificare, rulați scriptul de două ori și comparați fișierele (`md5`).

**Comparații de numere reale.** Un interval de 15 / 0,75 iese uneori 20,0000001 și pică testul „≤ 20”. Puneți o toleranță mică. Nu rotunjiți valorile pe care le folosiți mai departe (de exemplu orele-vehicul dintr-o acțiune), ci doar ce afișați.

**O metrică cerută care se comportă ciudat.** Dacă o metrică din fișă iese mai rău după adaptare, deși tot restul arată mai bine, nu o ascundeți. Uitați-vă de ce. La P4, de exemplu, ponderea curselor supraaglomerate poate crește tocmai pentru că adăugați curse pe linii care rămân pline. Explicația e un rezultat bun pentru raport.

**Verificați figurile.** Deschideți fiecare PNG înainte să-l puneți în raport. Etichete suprapuse, text negru pe fond negru, axe cu valori de tip 6×10⁰ apar mai des decât credeți.
