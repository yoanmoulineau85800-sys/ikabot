# Rapport de validation — 30 octobre 2026

Environnement : Linux x86_64, Python 3.12.14, PySide6 Essentials 6.12.0, Qt en mode `offscreen`, PyInstaller 6.22.3. Source moteur : `c300e506458007c1812a2225abea0db41c096d6f`. Les tests ne se connectent à aucun compte de jeu.

## Résultats exécutés

| Vérification | Résultat |
|---|---|
| Suite historique `tests/ikabot` et suite Desktop exécutées ensemble | **142 tests réussis**, **32 sous-tests réussis**, **1 test non exécuté** |
| Test non exécuté | DPAPI : réservé à Windows, explicitement ignoré sous Linux |
| Suite Desktop finale (incluse dans la validation complète) | **29 tests réussis**, **1 ignoré** |
| Avertissements historiques | 5 avertissements de dépréciation `fork()` dans un processus multithread du solveur ; non masqués |
| Démarrage Qt depuis les sources, navigation sur les 13 rubriques, arrêt | Réussi avec `desktop_app.py --smoke-test` |
| Vrai processus moteur depuis les sources | Formulaire de mot de passe atteint, annulation et arrêt vérifiés, sans connexion externe |
| Construction PyInstaller Linux de contrôle | Réussie ; il s'agit d'un exécutable Linux, pas Windows |
| Démarrage de cette distribution Linux | Réussi en mode `offscreen` avec `--smoke-test` |
| Processus moteur de la distribution Linux gelée | Réussi avec `--worker-smoke-test` : formulaire secret, annulation et arrêt, sans compte réel |
| Fichiers du moteur et dépôt original | Aucun changement suivi dans `ikabot/` ni dans le dépôt original |

## Ce que couvrent les tests Desktop

- Persistance des profils/préférences/événements SQLite, modification et suppression.
- Refus de stocker des identifiants dans les URLs de proxy.
- Absence de repli en clair pour un secret hors Windows.
- Existence et contrat réel de chaque configurateur exposé dans le catalogue.
- Transmission configurateur → tâche avec session et paramètres conservés, sur doubles contrôlés.
- Projection des champs des villes et mouvements, exclusion des données sensibles des projections.
- Occultation de secrets connus et d'en-têtes dans les textes éphémères.
- Navigation, thèmes, états vides sans données fictives, rendu d'une réponse simulée.
- Tri numérique, filtre et validation de plages dans les formulaires Qt.
- Vrai processus de connexion jusqu'au mot de passe, annulation et prévention de doublons.
- Validation locale des configurations de notifications sans envoi réseau.

## Tests réseau avec véritables sockets

Les tests démarrent un serveur HTTPS local et un proxy CONNECT dans un processus séparé. Le certificat de test est signé par une autorité de test locale et explicitement approuvé pour le test ; la vérification TLS reste activée.

1. Une requête HTTPS par le proxy atteint le serveur et produit le JSON attendu.
2. Le proxy coupe la connexion : la requête échoue et le nombre de requêtes reçues par l'origine reste inchangé.
3. Le proxy répond 502 : la requête échoue et aucun repli vers l'origine n'est observé.
4. Une tentative de socket directe vers l'origine et un datagramme DNS vers un autre port sont bloqués.
5. Un certificat non approuvé provoque une erreur TLS même si l'appelant fournit `verify=False`.
6. Une requête préparée HTTP est bloquée avant envoi.

Cela valide les cas locaux exécutés ; cela ne démontre pas un pare-feu infaillible, ni les comportements de tous les proxies ou postes Windows.

## Vérifications non exécutées

- Connexion réelle Gameforge/Ikariam, renouvellement réel des cookies et jetons, action en jeu et durée des automatisations.
- Réception réelle Telegram/Discord et interrogation ipify par un profil de jeu connecté.
- Tests d'API distante `tests/api`, séparés de la CI locale historique.
- Exécutable Windows, DPAPI réel, Windows 10/11, poste sans Python, tray Windows, proxy HTTPS/SOCKS et capture réseau Windows.
- Signature numérique ou installateur Windows ; le workflow fourni n'a pas été déclenché.

## Reproduction

Depuis la racine, avec les dépendances installées :

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q -p no:cacheprovider tests/ikabot tests/desktop
QT_QPA_PLATFORM=offscreen python desktop_app.py --smoke-test
QT_QPA_PLATFORM=offscreen python desktop_app.py --worker-smoke-test
python tools/audit_engine.py
python tools/collect_licenses.py
python -m PyInstaller --noconfirm packaging/IkabotDesktop.spec
QT_QPA_PLATFORM=offscreen dist/IkabotDesktop/IkabotDesktop --smoke-test
QT_QPA_PLATFORM=offscreen dist/IkabotDesktop/IkabotDesktop --worker-smoke-test
```

Sous Windows, `tools/build_windows.ps1` exécute les tests dont DPAPI, construit la distribution puis vérifie le lancement et le processus moteur du binaire avant de créer l'archive. Ce script est préparé mais son succès sur Windows n'est pas affirmé.
