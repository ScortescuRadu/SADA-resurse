# Rulări repetate și statistică

Când sistemul are elemente aleatoare (încetinire aleatoare, mutații, cerere stochastică), o singură rulare nu spune mare lucru: altă sămânță (seed) poate da alt rezultat. De aceea fișa cere cel puțin 20 de rulări (30 la tema P2) și raportarea cu medie și abatere standard.

## Seed-uri

- În config, `experiment.base_seed` și `experiment.n_runs` definesc seed-urile: `base_seed`, `base_seed + 1`, ...
- Fiecare rulare primește un generator propriu, `rng = np.random.default_rng(seed)`. Trimiteți-l ca parametru tuturor funcțiilor care au nevoie de numere aleatoare. Nu folosiți `random.random()` sau `np.random.rand()` direct, pentru că depind de o stare globală și rezultatele nu mai pot fi refăcute.
- Când comparați două variante, folosiți **aceleași** seed-uri pentru amândouă. Diferențele vin atunci din variante, nu din noroc.

## Ce raportați

Pentru fiecare combinație scenariu × variantă:

- **media** și **abaterea standard** (cu `ddof=1`, adică abaterea de eșantion), scrise ca „124,3 ± 8,7 s”;
- opțional, **intervalul de încredere de 95%** pentru medie; `sada.stats.summarize` îl calculează.

Abaterea standard spune cât de mult variază rezultatele de la o rulare la alta. Intervalul de încredere spune cât de sigur sunteți pe medie. Spuneți în text pe care îl folosiți.

## Când e o diferență reală

Dacă media variantei adaptive e 118 s și a referinței 124 s, diferența poate fi întâmplătoare. Două unelte simple:

- **Testul Mann–Whitney U** (`sada.stats.compare`) nu presupune distribuții normale și e folosit des în lucrările GECCO. Un p sub 0,05 sugerează că diferența nu e întâmplătoare.
- **Mărimea efectului A12** (Vargha–Delaney) arată cât de mare e diferența: 0,5 înseamnă nicio diferență, iar valori în jur de 0,56, 0,64 și 0,71 sunt considerate efect mic, mediu și mare.

Un rezultat semnificativ statistic, dar cu efect mic, nu e neapărat important în practică. Spuneți ambele lucruri.

```python
from sada.stats import compare
a = df[(df.scenario == "ridicata") & (df.variant == "adaptiv")]["travel_time_mean"]
b = df[(df.scenario == "ridicata") & (df.variant == "fix")]["travel_time_mean"]
print(compare(a, b))   # {'U': ..., 'p_value': ..., 'A12': ...}
```

## Greșeli frecvente

- **Cele mai bune 20 din 50 de rulări.** Raportați toate rulările făcute pentru o configurație.
- **Pragurile alese pe aceleași rulări pe care testați.** Dacă reglați pragurile controllerului pe seed-urile 0–19, testați pe alte seed-uri (de exemplu 1000–1019) sau spuneți clar în secțiunea de limite.
- **Perioada de încălzire inclusă în metrici.** Primele minute de simulare reflectă starea inițială. Scoateți-le din calcul și spuneți cât ați scos.
- **Medii fără dispersie.** Un grafic cu bare fără abatere standard nu poate fi interpretat. Boxplot-urile din `scripts/make_figures.py` arată toată distribuția.
