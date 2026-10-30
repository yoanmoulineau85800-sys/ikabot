# Ikabot Desktop — première version de développement

Application PySide6 basée sur le moteur Ikabot 7.7.2 conservé intégralement. Navigation française, profils SQLite, données réelles des villes/mouvements, assistants graphiques des commandes, proxy strict au niveau du processus, sessions Windows protégées par DPAPI, thèmes et zone de notification.

**Ce n'est pas encore une version Windows finale validée.** Les textes internes du moteur sont partiellement traduits, les actions en jeu nécessitent une validation avec un compte de test, et plusieurs intégrations sont explicitement exclues. Aucun `.exe` Windows n'a été compilé sous Linux.

- [Guide français](docs/GUIDE_FR.md)
- [Audit et tableau de toutes les fonctions](docs/AUDIT.md)
- [Inventaire détaillé des paramètres et invites](docs/INVENTAIRE.json)
- [Architecture](docs/ARCHITECTURE.md)
- [Rapport des tests](docs/TESTS.md)
- [Licences](docs/LICENCES.md)
- [Travail terminé et restant](docs/AVANCEMENT.md)
- [Capture du démarrage sans données fictives](docs/interface-demarrage.png)

## Développement

Python 3.12, depuis la racine :

```bash
python -m venv .venv-desktop
# Windows : .venv-desktop/Scripts/python.exe
.venv-desktop/bin/python -m pip install -e '.[webServer]' -r requirements-desktop.txt
.venv-desktop/bin/python desktop_app.py
.venv-desktop/bin/python -m pytest tests/ikabot tests/desktop
```

Sur un serveur Linux sans affichage : utiliser `QT_QPA_PLATFORM=offscreen` pour les tests Qt et le test `desktop_app.py --smoke-test`. Une vraie session graphique est nécessaire pour l'utilisation interactive et l'icône de notification.

Pour compiler sous Windows : exécuter `tools/build_windows.ps1` depuis PowerShell ou déclencher manuellement le workflow **Ikabot Desktop Windows** après avoir placé cette branche sur votre dépôt. Le script produit `dist/IkabotDesktop-Windows-x64.zip`. Les utilisateurs finaux extraient l'archive et lancent l'exécutable, sans Python.
