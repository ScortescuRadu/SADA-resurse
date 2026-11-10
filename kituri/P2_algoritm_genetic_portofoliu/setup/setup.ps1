# Instalează mediul de lucru pe Windows (PowerShell).
#   powershell -ExecutionPolicy Bypass -File setup\setup.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$py = $env:PYTHON
if (-not $py) {
    if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" } else { $py = "python" }
}
& $py -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "E nevoie de Python 3.10 sau mai nou (https://www.python.org/downloads/). La instalare bifați 'Add python.exe to PATH'."
}

if (-not (Test-Path ".venv")) {
    Write-Host ">> Creez mediul virtual .venv"
    & $py -m venv .venv
}
$venvPy = Join-Path ".venv" "Scripts\python.exe"

Write-Host ">> Instalez dependențele (poate dura câteva minute)"
& $venvPy -m pip install --upgrade pip wheel
& $venvPy -m pip install -r requirements.txt
& $venvPy -m pip install -e .

Write-Host ">> Verific mediul"
& $venvPy scripts\check_env.py

Write-Host ""
Write-Host "Gata. În fiecare terminal nou, activați mediul:"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "(dacă PowerShell refuză: Set-ExecutionPolicy -Scope Process Bypass)"
Write-Host "Apoi încercați exemplul:"
Write-Host "    python examples\toy_mapek.py"
