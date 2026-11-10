# Mediul de lucru și Git

Ghidul acesta acoperă lucrurile care de obicei consumă o seară întreagă când apar în săptămâna 13: mediul virtual, dependențele, Git-ul și problemele tipice pe Windows.

## Ce aveți nevoie

- **Python 3.10 sau mai nou.** Verificați cu `python --version` (sau `py --version` pe Windows). Pe Windows, la instalare bifați „Add python.exe to PATH”.
- **Git.** Pe Windows, Git for Windows vine și cu Git Bash, în care merg scripturile `.sh`.
- **Un editor.** VS Code cu extensia Python e suficient. Selectați interpretorul din `.venv` (Ctrl+Shift+P → „Python: Select Interpreter”).

## Instalarea, pe scurt

```bash
# Linux / macOS / WSL / Git Bash
bash setup/setup.sh
source .venv/bin/activate
```

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File setup\setup.ps1
.\.venv\Scripts\Activate.ps1
```

Scriptul creează mediul virtual `.venv`, instalează pachetele din `requirements.txt`, instalează codul din `src/` în mod editabil (modificările voastre se văd imediat, fără reinstalare) și rulează `scripts/check_env.py`.

## De ce mediu virtual

Fiecare proiect are propriile versiuni de pachete. Dacă instalați totul global, mai devreme sau mai târziu un alt proiect vă strică versiunile. Mediul virtual e un folder (`.venv`) cu un Python separat. Îl activați la fiecare terminal nou; promptul începe atunci cu `(.venv)`.

## Fixarea versiunilor

`requirements.txt` din arhivă are versiuni minime. Când proiectul vostru merge, înghețați versiunile exacte, ca să poată fi refăcut peste o lună:

```bash
pip freeze > requirements.lock.txt
```

Puneți `requirements.lock.txt` în depozit și menționați-l în README. Secțiunea „Date și configurare” din raport cere versiunile; le luați de aici.

## Git în cinci comenzi

```bash
git init                         # o singură dată
git add -A                       # pregătește toate modificările
git commit -m "NaSch pe inel"    # salvează un pas, cu un mesaj care spune ce ați făcut
git remote add origin <URL>      # o singură dată, după ce creați depozitul pe GitHub/GitLab
git push -u origin main          # trimite pe server
```

Pentru echipe de doi: fiecare lucrează pe fișierele lui când se poate, faceți `git pull` înainte să începeți și `git push` când terminați. Dacă apare un conflict, Git vă arată ambele variante în fișier, între `<<<<<<<` și `>>>>>>>`; păstrați ce trebuie, ștergeți marcajele, apoi `git add` și `git commit`.

`.gitignore` din arhivă exclude deja `.venv/`, `results/` și `data/raw/`. Rezultatele se refac cu scripturile, iar datele brute se descarcă din nou; nu le încărcați în depozit.

## Probleme frecvente

| Simptom | Cauză probabilă | Ce faceți |
|---|---|---|
| `ModuleNotFoundError: No module named 'sada'` | mediul nu e activat sau lipsește `pip install -e .` | activați `.venv`, apoi `pip install -e .` |
| PowerShell: „running scripts is disabled” | politica de execuție | `Set-ExecutionPolicy -Scope Process Bypass` |
| `python` deschide Microsoft Store | aliasul Windows | folosiți `py`, sau dezactivați aliasul din Setări → Aplicații → Aliasuri de execuție |
| Figurile nu se deschid | scripturile salvează direct în fișiere | căutați în `results/figures/` |
| Diacriticele apar stricat în fișiere | codificarea implicită pe Windows | scripturile scriu UTF-8; deschideți fișierele cu un editor care detectează UTF-8 |
| Merge la mine, nu merge la colegul | versiuni diferite de pachete | `pip install -r requirements.lock.txt` |

## Verificarea finală

Înainte de predare, clonați depozitul într-un folder nou, rulați setup-ul de la zero și apoi comanda din README. Dacă figurile ies la fel, reproductibilitatea e în regulă.
