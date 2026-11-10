# Datele pentru P2

## Ce primiți în pachetul disciplinei

Folderul `p2_portofoliu/`: fișiere JSON cu schemele, costurile și beneficiile estimate pentru ramurile A, B și C (unitățile sunt explicate în DATA.md din pachet), plus un șablon de fișier cu scenariile de schimbare. Copiați-l în `data/p2_portofoliu/`.

**Important:** beneficiile provin dintr-un model de evaluare simplificat. Nu sunt valori măsurate, iar raportul trebuie să spună acest lucru.

## Instanțele de dezvoltare

Până primiți pachetul, sau ca să testați pe probleme de alte dimensiuni:

```bash
python scripts/prepare_data.py
```

generează în `data/dev/` instanțe **sintetice** (valori inventate, doar pentru dezvoltare):

| Fișier | Ramura | Tip | n |
|---|---|---|---|
| `dev_A_12.json`, `dev_A_20.json`, `dev_A_40.json` | A, intervenții urbane | binar | 12, 20, 40 |
| `dev_B_12.json` | B, transport public | întreg (ore-vehicul pe linie) | 12 linii |
| `dev_C_20.json` | C, rețea velo | binar, cu dependențe între faze | 10 zone × 2 faze |

și pentru fiecare un fișier `changes_<nume>.json` cu trei schimbări (buget −30%, o intervenție eliminată, ponderi 50/50).

## Formatul (instanțele de dezvoltare)

```json
{
  "name": "dev_A_20", "kind": "binary", "branch": "A",
  "budget": 3338000.0,
  "items": [
    {"id": "S01", "label": "bandă de biciclete #1", "cost": 251000.0, "benefit": 412.3, "equity": 95.1},
    ...
  ]
}
```

- **Ramura B** (`"kind": "integer"`): fiecare linie are `lower`, `upper` (ore-vehicul), `benefit` (a) și `saturation` (b); beneficiul liniei e a · (1 − e^(−x/b)), adică fiecare oră-vehicul în plus aduce mai puțin decât precedenta. `budget` este totalul de ore-vehicul (constrângerea de flotă).
- **Ramura C**: elementele pot avea `"requires": "<id>"` (faza 2 dintr-o zonă cere faza 1).

Dacă fișierele din pachet au alt format, adaptați doar `Problem.from_json` din `src/sada/p2/problem.py`; restul codului lucrează cu atributele clasei.

## Scenariile de schimbare

```json
{"changes": [
  {"generation": 100, "type": "budget_scale", "factor": 0.7},
  {"generation": 200, "type": "remove_item", "id": "S07"},
  {"generation": 300, "type": "weights", "w_benefit": 0.5, "w_equity": 0.5}
]}
```

Generațiile pot fi schimbate. Fișa cere cel puțin două schimbări în timpul rulării.

## Ce notați în data/DATA.md

Sursa fiecărui fișier (pachetul disciplinei sau generat de voi, cu seed-ul), data, licența și precizarea că beneficiile sunt estimări de model.
