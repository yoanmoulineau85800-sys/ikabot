$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($env:OS -ne 'Windows_NT') { throw 'La compilation .exe doit être exécutée sous Windows.' }
py -3.12 -m venv .venv-desktop
if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 est nécessaire sur la machine de compilation.' }
$python = Join-Path $PWD '.venv-desktop/Scripts/python.exe'
& $python -m pip install -e '.[webServer]' -r requirements-desktop.txt
if ($LASTEXITCODE -ne 0) { throw 'Installation des dépendances échouée.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dépendances incohérentes.' }
& $python -m pytest -q -p no:cacheprovider tests/ikabot tests/desktop
if ($LASTEXITCODE -ne 0) { throw 'Les tests ont échoué ; distribution interrompue.' }
& $python tools/collect_licenses.py
if ($LASTEXITCODE -ne 0) { throw 'Collecte des licences échouée.' }
& $python -m PyInstaller --noconfirm --clean packaging/IkabotDesktop.spec
if ($LASTEXITCODE -ne 0) { throw 'Compilation PyInstaller échouée.' }
$exe = Join-Path $PWD 'dist/IkabotDesktop/IkabotDesktop.exe'
$smoke = Start-Process -FilePath $exe -ArgumentList '--smoke-test' -PassThru
if (-not $smoke.WaitForExit(30000)) { $smoke.Kill(); throw 'Le test de démarrage a dépassé 30 secondes.' }
if ($smoke.ExitCode -ne 0) { throw 'Le programme compilé ne démarre pas correctement.' }
$workerSmoke = Start-Process -FilePath $exe -ArgumentList '--worker-smoke-test' -PassThru
if (-not $workerSmoke.WaitForExit(30000)) { $workerSmoke.Kill(); throw 'Le test du moteur compilé a dépassé 30 secondes.' }
if ($workerSmoke.ExitCode -ne 0) { throw 'Le processus moteur compilé ne fonctionne pas correctement.' }
Compress-Archive -Path 'dist/IkabotDesktop' -DestinationPath 'dist/IkabotDesktop-Windows-x64.zip' -Force
Get-FileHash 'dist/IkabotDesktop-Windows-x64.zip' -Algorithm SHA256 | Format-List
Write-Host 'Distribution prête. Extraire tout le dossier puis ouvrir IkabotDesktop.exe.'
