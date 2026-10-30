# Guide d'utilisation — Ikabot Desktop 0.1

Cette première version raccorde une interface graphique au moteur existant. Elle n'est pas encore une version Windows finale validée : les assistants contiennent encore des textes anglais et les parcours en jeu n'ont pas été testés avec un vrai compte. Consulter `AUDIT.md` pour la disponibilité de chaque fonction.

## Démarrer sous Windows

Une fois la distribution Windows produite, extraire **tout** le dossier `IkabotDesktop-Windows-x64.zip` dans un dossier accessible en écriture, puis ouvrir `IkabotDesktop.exe`. Python n'est pas nécessaire sur le poste utilisateur. Ne pas déplacer l'exécutable seul : le dossier `_internal` contient Qt et le moteur. Windows 10/11 x64 sont les cibles prévues, à valider sur des postes réels. La version n'est pas signée numériquement.

L'environnement actuel est Linux : aucun `.exe` Windows n'a été compilé ici. Le script `tools/build_windows.ps1` réalise les tests, la compilation et l'archive sur un poste de compilation Windows équipé de Python 3.12. Le workflow GitHub **Ikabot Desktop Windows** fournit la même opération manuelle ; il n'a pas été déclenché depuis cette tâche.

## Première connexion

1. Ouvrir **Comptes et profils**, puis **Ajouter un profil**.
2. Donner un nom au profil et l'adresse du compte Gameforge. Le serveur attendu est facultatif ; s'il est renseigné, saisir son nom d'hôte exact (exemple de format : `s1-fr.ikariam.gameforge.com`). Desktop refuse les actions si le serveur choisi dans le lobby ne correspond pas.
3. Si nécessaire, renseigner un proxy HTTP, HTTPS ou SOCKS5h sans identifiants. Les proxies authentifiés ne sont pas encore pris en charge. Laisser ce champ vide pour utiliser le réseau de l'environnement.
4. Sélectionner le profil en haut, puis **Se connecter**. Saisir le mot de passe dans la fenêtre masquée. Les éventuelles étapes supplémentaires de connexion apparaissent dans l'assistant.
5. Choisir le compte/serveur réel demandé par le moteur. Les choix sont ceux retournés par Gameforge, pas une liste simulée.
6. Cliquer sur **Actualiser**. Les villes, ressources, niveaux des bâtiments, constructions et mouvements proviennent du moteur. Leur date de dernière lecture est affichée ; ce ne sont pas des valeurs mises à jour en continu sans requête.

L'accès au jeton de connexion du moteur dépend d'une API externe découverte par DNS. Desktop exige HTTPS pour cette API. Si elle n'est disponible qu'en HTTP, l'obtention automatique échoue et le moteur peut proposer son parcours manuel. Ne jamais publier de jeton ou cookie dans une capture, un ticket ou un journal.

## Utiliser les fonctions

Les rubriques du menu regroupent les commandes vérifiées dans le code. **Configurer…** ouvre les étapes originales dans des formulaires graphiques. Les limites numériques et choix restent validés par le moteur. Certains champs libres sont masqués par précaution, notamment lorsqu'ils peuvent recevoir un secret. Les textes non traduits restent visibles et identifiés ; ne valider aucune opération dont l'effet n'est pas compris.

La tâche est exécutée dans le processus du profil. Le suivi du moteur est visible en bas de fenêtre ; les opérations ne bloquent pas la navigation. Une opération à la fois est possible par profil. Une automatisation longue occupe donc ce profil jusqu'à son arrêt. D'autres profils distincts restent utilisables. Desktop refuse deux profils simultanés pour le même compte et serveur ; un serveur non précisé entraîne une prévention plus stricte.

Les tableaux permettent de trier sur les en-têtes, filtrer toutes les colonnes, déplacer les colonnes et les masquer avec un clic droit sur l'en-tête. La disposition des colonnes est conservée. Les thèmes se choisissent dans **Paramètres** et sont conservés.

## Notifications

Dans **Alertes et notifications**, configurer le jeton et l'identifiant de conversation Telegram ou l'URL officielle de webhook Discord. L'enregistrement seul n'envoie aucun message. Les boutons de test du moteur permettent ensuite de demander explicitement un envoi. Ces tests et les alertes réelles nécessitent des services configurés ; ils n'ont pas été exécutés ici. Certains helpers du moteur absorbent les erreurs d'envoi : vérifier la réception dans le canal, ne pas déduire une livraison du seul état « Opération terminée ».

## Proxy et état réseau

Le choix du proxy s'applique avant l'authentification, au lobby et aux requêtes métier. En cas de panne, les requêtes échouent au lieu de sélectionner une connexion directe. **Vérifier l'adresse IP publique** interroge ipify par le chemin réseau du profil connecté. Le résultat décrit cette requête, pas une certification de toutes les communications Windows.

Les tests automatiques locaux vérifient une panne et une erreur de proxy CONNECT ainsi que le blocage d'une socket directe et d'un datagramme DNS. Ils ne prouvent pas le comportement de tous les fournisseurs de proxy. Une validation Windows réelle est encore nécessaire.

## Arrière-plan et arrêt

Si Windows offre une zone de notification, fermer la fenêtre la masque et laisse les processus actifs. Le menu de l'icône propose **Ouvrir**, **Arrêter toutes les tâches** et **Quitter complètement**. Sans zone de notification, fermer arrête l'application.

**Arrêter le profil** interrompt son processus et sa session. Une requête déjà reçue par le jeu peut avoir produit son effet. Vérifier l'état réel du jeu avant tout nouveau lancement. Les automatisations interrompues ne sont jamais relancées automatiquement.

## Données et protection

Les données locales sont dans le dossier indiqué sous **Paramètres**, normalement `%LOCALAPPDATA%/IkabotDesktop/Ikabot Desktop` selon Qt. SQLite contient les noms, e-mails, serveurs, proxies sans identifiants, préférences et événements. Ces métadonnées ne sont pas chiffrées. Les fichiers de session des profils sont chiffrés avec DPAPI sous Windows. Ils sont liés à l'utilisateur Windows courant et ne doivent pas être considérés comme portables vers une autre machine. Les mots de passe ne sont pas enregistrés par Desktop.

Sous Linux, les sessions et réglages sensibles restent seulement en mémoire. La suppression d'un profil déconnecté supprime son dossier de sessions ; elle ne supprime pas son compte Gameforge. Les sorties brutes du moteur ne sont pas conservées dans les journaux. L'historique contient les événements récents et les classes d'erreur utiles au diagnostic.

## Mise à jour

1. Arrêter les tâches et quitter complètement.
2. Conserver une sauvegarde du dossier de données, uniquement dans un emplacement privé. Les sessions DPAPI restent liées à Windows.
3. Extraire la nouvelle distribution dans un nouveau dossier, sans mélanger les bibliothèques de deux versions.
4. Ouvrir la nouvelle application et vérifier les profils, puis se reconnecter si nécessaire.

La base actuelle n'a pas encore de mécanisme de migration de schéma au-delà de la création initiale. Une évolution de schéma devra fournir et tester sa migration avant livraison. Le bouton de mise à jour CLI du moteur est volontairement exclu du programme gelé.
