# Licences et redistribution

- **Ikabot** : MIT, copyright 2018 Physics. Le fichier LICENSE original est conservé. Aucun fichier source du moteur n'a été modifié.
- **Code Desktop de cette copie** : distribué sous la licence MIT jointe au dépôt, sous réserve des droits des dépendances.
- **PySide6 / Qt / Shiboken** : options LGPLv3, GPLv3 ou commerciale selon composants et choix de licence. Les modules utilisés sont QtCore, QtGui et QtWidgets via les bibliothèques dynamiques. Le paquet PyInstaller est en dossier `onedir`, sans UPX ; conserver les DLL remplaçables, notices et textes de licence. Ne pas interdire l'analyse nécessaire au débogage des modifications des bibliothèques LGPL. Vérifier les obligations exactes de la version redistribuée et fournir les références/sources correspondantes selon les licences applicables.
- **PyInstaller** : GPL avec exception pour les applications distribuées ; vérifier la notice de la version utilisée.
- **Autres dépendances** : requests, urllib3, certifi, cryptography, cffi, psutil, python-dotenv, Flask et dépendances transitives. Le script `tools/collect_licenses.py` copie les notices disponibles dans les métadonnées installées et crée un index avant assemblage. Les tests/outils présents dans l'index peuvent dépasser les dépendances réellement embarquées.
- **Poids du modèle local** : le dépôt contient `ikabot/assets/local_purepython_decaptcha_weights.bin`. La présence de la licence MIT à la racine ne documente pas à elle seule la provenance des données d'entraînement ou d'éventuels droits tiers. Vérifier les droits et notices de ce modèle avant redistribution publique. Aucun droit supplémentaire n'est présumé.
- **Services** : Gameforge/Ikariam, Telegram, Discord et les APIs externes ont leurs propres conditions. Une licence de code n'autorise ni ne garantit l'usage d'un compte ou du service.

Les notices collectées facilitent la revue ; elles ne remplacent pas la vérification des obligations de la distribution finale Windows. Aucun artefact Windows n'est signé ou publié dans cette tâche.
