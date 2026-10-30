# Exécuter avec PyInstaller depuis la racine du dépôt.
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PySide6.QtCore import QLibraryInfo

root = Path(SPECPATH).parent
datas = collect_data_files('ikabot')
datas += [(str(root / 'LICENSE'), 'licences'), (str(root / 'docs'), 'docs')]
licences = root / 'packaging' / 'licences'
if licences.exists():
    datas += [(str(licences), 'licences/dependances')]
translation = Path(QLibraryInfo.path(QLibraryInfo.TranslationsPath)) / 'qtbase_fr.qm'
if translation.exists():
    datas.append((str(translation), 'PySide6/Qt/translations'))

a = Analysis([str(root / 'desktop_app.py')], pathex=[str(root)],
             binaries=[], datas=datas, hiddenimports=collect_submodules('ikabot'),
             hookspath=[], runtime_hooks=[],
             excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
                       'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtPdf'],
             noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='IkabotDesktop',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='IkabotDesktop')
