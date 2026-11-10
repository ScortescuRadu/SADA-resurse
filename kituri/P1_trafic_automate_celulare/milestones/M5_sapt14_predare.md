# M5 (săptămâna 14): predarea și prezentarea

## Ce predați

Raportul final (PDF, 8–12 pagini fără anexe), prezentarea (8–10 diapozitive, 10 minute) și depozitul de cod.

## Ce trebuie să aveți

- [ ] `python scripts/verify_submission.py` trece: clonare curată, instalare, teste, experiment scurt, fără chei sau date fără sursă.
- [ ] `requirements.lock.txt` în depozit (`pip freeze > requirements.lock.txt`).
- [ ] `data/DATA.md` complet: sursă, dată, licență pentru fiecare fișier.
- [ ] Raportul final copiat în depozit ca `raport/raport.pdf` (așa îl caută `milestone_check.py M5`).
- [ ] README-ul proiectului vostru (nu cel al kitului): ce face, cum se instalează, comanda care reface tot, ce ați adăugat.
- [ ] Toate testele trec, fără teste sărite.
- [ ] Lista din `raport/CHECKLIST.md` bifată.
- [ ] Prezentarea repetată cu cronometrul; înregistrarea de rezervă a demonstrației.

## Demonstrația finală

Propunere pentru această temă: incidentul de 120 s: tronsonul se blochează, controllerul schimbă regula, viteza revine; aceeași figură cu varianta fixă alături. Maximum 2 minute; spuneți publicului dinainte ce trebuie să vadă. Scheletul prezentării: `prezentare/SCHELET_PREZENTARE.md`.

## Cod pentru etapa asta

| Ce | Unde |
|---|---|
| verificarea finală pe o copie curată | `python scripts/verify_submission.py` (sau `--fast`, fără experiment) |
| testele la fiecare push (opțional, GitHub) | `.github/workflows/tests.yml` |
| figurile în PNG pentru diapozitive | `results/figures/*.png` (le face `make_figures.py`) |

## Întrebări la care să știți să răspundeți

Vedeți secțiunea „Întrebări de verificare înainte de prezentare” din `GHID.md`. Fiecare membru trebuie să poată explica orice rând de cod și orice figură.

## Greșeli tipice

- Rezultatele din raport nu se mai obțin cu codul predat (s-a schimbat ceva după ultima rulare). Rulați `run_all.py` și `make_figures.py` o ultimă dată, după ultima modificare de cod.
- Date necomise de care depinde `run_all.py`. `verify_submission.py` le prinde.
- Prezentarea depășește 10 minute pentru că demonstrația pornește de la zero.
