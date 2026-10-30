# Avancement et limites

## Réalisé et vérifiable dans le code

- Copie distincte du moteur, branche `desktop/francais`, référence officielle identifiée.
- Audit reproductible des 46 entrées cataloguées et des 258 définitions métier de premier niveau.
- Architecture séparant interface, adaptation moteur, supervision, réseau et stockage.
- Fenêtre Qt, 13 rubriques, navigation française, thèmes sombre/clair persistants.
- Profils ajoutables, modifiables, supprimables ; stockage SQLite sans identifiants secrets.
- Connexion via le moteur, formulaires à la place de stdin/getpass ; vérification du serveur attendu.
- Réutilisation des configurateurs et tâches existants, avec les validations métier conservées.
- Projections réelles villes, ressources, bâtiments, constructions et mouvements ; tri et filtre.
- Une opération par profil, processus indépendants, verrou de l'application et prévention des doublons.
- Suivi éphémère du moteur, états structurés persistants et erreurs visibles.
- Configuration native des notifications sans envoi implicite, stockage compatible avec le moteur.
- Proxy imposé avant le lobby, HTTPS/TLS obligatoire, délais bornés, restriction des sockets du processus.
- Stockage DPAPI implémenté sous Windows ; absence de repli persistant en clair sous Linux.
- Zone de notification, arrêt des processus possédés, aucune reprise automatique à risque.
- Tests unitaires, interface, processus et réseau local réel ; scripts d'assemblage Windows et workflow manuel.
- Documentation française, notices de licences et procédure de mise à jour.

## À terminer avant une version destinée à un utilisateur non technique

- Traduire tous les assistants et noms internes du moteur ; les entrées inconnues restent affichées dans leur langue d'origine.
- Valider avec un compte de test chaque assistant, ses résultats et l'authentification Gameforge réelle, sans automatisation non consentie.
- Compiler sur Windows 10/11 x64, tester DPAPI, première connexion, SSL, changement d'utilisateur, système de fichiers et zone de notification.
- Tester le proxy HTTPS/SOCKS, IPv6, DNS, coupures à chaque phase de connexion et capture réseau du processus sur Windows.
- Tester le binaire Windows sur une machine sans Python et vérifier les bibliothèques Qt remplaçables.
- Mettre en place une signature de code et éventuellement un installateur ; aucune signature n'est simulée.
- Plusieurs tâches simultanées par compte, ordonnanceur natif, restauration après vérification de non-duplication et migrations de base.
- Intégrations restantes : serveur web, modules personnalisés, outils développeur, transfert sécurisé de cookies.
- Améliorer les diagnostics structurés sans remettre les journaux HTTP sensibles ; auditer les sorties du moteur avant exposition plus large.
- Vérifier les obligations exactes de redistribution et la provenance des poids du modèle.

Les fonctions exclues sont conservées dans le moteur et documentées dans le catalogue. Aucune donnée de démonstration ni résultat de test externe supposé ne remplace ces travaux.
