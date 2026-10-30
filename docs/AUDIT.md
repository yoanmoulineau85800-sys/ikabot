# Audit Ikabot Desktop

Source officielle : https://github.com/Ikabot-Collective/ikabot
Commit analysé : `c300e506458007c1812a2225abea0db41c096d6f` (moteur 7.7.2).
Le checkout original /workspace/ikabot est conservé. Le développement utilise une copie indépendante et la branche desktop/francais.

## Architecture constatée

`command_line.py` sélectionne les fonctions ; `web/session.py` gère Gameforge, lobby, comptes, cookies, renouvellement et requêtes Ikariam. `helpers/sessionStorage.py` gère les fichiers de sessions ; `helpers/decorators.py` sépare les configurateurs interactifs et les tâches ; `helpers/process.py` suit les processus. `pedirInfo.py` valide les choix et découvre les villes ; `getJson.py` analyse les réponses. Les helpers naval/resources/planRoutes réutilisent les mêmes sessions. Les captchas locaux utilisent des poids binaires et éventuellement multiprocessing. `apiComm.py`, `dns.py` et `botComm.py` utilisent aussi requests en dehors de Session.

## Entrées fonctionnelles et statut

Les paramètres des configurateurs sont principalement session, event, stdin_fd, predetermined_input. Les paramètres métier sont obtenus par leurs assistants : le JSON joint inventorie chaque appel read et ses contraintes, sans inventer de formulaire statique. Leur retour dict est transmis à la tâche d'origine. « Assistant » signifie raccordé au code, contrat testé et formulaires réels ; cela ne signifie pas validation en jeu. Sans compte de test, tous les parcours réseau métier restent à valider.

| Fonction | Module source | Paramètres du configurateur | Paramètres de tâche | Dépendances | Faisabilité / statut |
|---|---|---|---|---|---|
| File de construction | `ikabot/function/constructionList.py` | constructionList(session, event, stdin_fd, predetermined_input) | do_it(session, city_id, city_name, buildings, shipments, expand_overall, wait_resources, construction_queue, total_time) | decimal, functools, hashlib, html, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, ikabot.web.session, json, math, random, re, requests, threading, time, traceback, urllib.parse | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Envoyer des ressources | `ikabot/function/sendResources.py` | sendResources(session, event, stdin_fd, predetermined_input) | do_it(session, routes, useFreighters) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Répartir les ressources | `ikabot/function/distributeResources.py` | distributeResources(session, event, stdin_fd, predetermined_input) | do_it(session, routes, useFreighters, resource) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.process, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| État du compte | `ikabot/function/getStatus.py` | getStatus(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | decimal, hashlib, ikabot.config, ikabot.function.autoPirate, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.market, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.resources, ikabot.helpers.varios, json, os, re, time | Remplacé par le tableau de bord natif. |
| Activer le sanctuaire | `ikabot/function/activateShrine.py` | activateShrine(session, event, stdin_fd, predetermined_input) | do_it(session, godids, mode, times, selected_gods, wait_time) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.resources, ikabot.helpers.varios, json, re, time | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Connexion quotidienne | `ikabot/function/loginDaily.py` | loginDaily(session, event, stdin_fd, predetermined_input) | do_it(session, wine_city, wood_city, luxury_city, favour_tasks, collect_ambrosia) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.signals, ikabot.helpers.varios, re, sys, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Surveiller les attaques | `ikabot/function/alertAttacks.py` | alertAttacks(session, event, stdin_fd, predetermined_input) | do_it(session, minutes) | ikabot.function.vacationMode, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.signals, ikabot.helpers.varios, threading, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Surveiller les réserves de vin | `ikabot/function/alertLowWine.py` | alertLowWine(session, event, stdin_fd, predetermined_input) | do_it(session, hours, auto_transfer, transfer_amount) | datetime, decimal, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, json, re, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Acheter des ressources | `ikabot/function/buyResources.py` | buyResources(session, event, stdin_fd, predetermined_input) | do_it(session, city, offers, amount_to_buy) | decimal, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.market, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, json, math, re, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Vendre des ressources | `ikabot/function/sellResources.py` | sellResources(session, event, stdin_fd, predetermined_input) | do_it(session, mode, amount_to_sell=None, offers=None, resource_type=None, city_to_buy_from=None, price=None, sell_market_capacity=None, city=None) | decimal, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.market, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.signals, ikabot.helpers.varios, json, math, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Faire un don | `ikabot/function/donate.py` | donate(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.resources, ikabot.helpers.varios, json, re | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Automatiser les dons | `ikabot/function/donationBot.py` | donationBot(session, event, stdin_fd, predetermined_input) | do_it(session, cities_ids, cities_dict, waiting_time, donate_method) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Activer le mode vacances | `ikabot/function/vacationMode.py` | vacationMode(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, sys | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Activer un miracle | `ikabot/function/activateMiracle.py` | activateMiracle(session, event, stdin_fd, predetermined_input) | do_it(session, island, iterations) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.signals, ikabot.helpers.varios, json, re, traceback, unicodedata | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Recruter des troupes et des navires | `ikabot/function/trainArmy.py` | trainArmy(session, event, stdin_fd, predetermined_input) | do_trainArmy(session, city, tranings, trainTroops, replicate, countRepeat, cityTrainings, units) | asyncio, copy, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, json, re, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Déplacer les troupes et les navires | `ikabot/function/stationArmy.py` | stationArmy(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.varios, re | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Améliorer les unités | `ikabot/function/UpgradeUnits.py` | UpgradeUnits(session, event, stdin_fd, predetermined_input) | execute_sequential_upgrades(session, jobs) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, ikabot.web.session, json, os, re, sys, threading, time | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Consulter les armées | `ikabot/function/viewArmy.py` | viewArmy(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.varios, json, os, re, sys | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Consulter les mouvements | `ikabot/function/shipMovements.py` | shipMovements(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | decimal, ikabot, ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.varios, json, math, re, sys | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Construire ou améliorer un bâtiment | `ikabot/function/constructBuilding.py` | constructBuilding(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.varios, json, re | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Mettre à jour le moteur | `ikabot/function/update.py` | update(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, sys | La mise à jour se fait par remplacement de la distribution complète. |
| Serveur web du moteur | `ikabot/function/webServer.py` | webServer(session, event, stdin_fd, predetermined_input, port=None) | do_webServer(session, port, local_network_ip) | base64, datetime, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.logging, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.varios, io, json, logging, pickle, re, requests, signal, socket, sys, threading, time, traceback, urllib.parse | À intégrer : serveur lié à la session, exposition et arrêt à sécuriser. |
| Automatiser la piraterie | `ikabot/function/autoPirate.py` | autoPirate(session, event, stdin_fd, predetermined_input) | do_pirate_missions(session, pirateCount, pirateSchedule, pirateMissionChoice, pirateMissionDayChoice, pirateMissionNightChoice, dayStart, dayEnd, nightStart, nightEnd, autoConvert, convertPerMission, maxRandomWaitingTime, piracyCities) | base64, ikabot.config, ikabot.helpers.apiComm, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.varios, json, re, requests, sys, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Effectuer une recherche | `ikabot/function/research.py` | research(session, event, stdin_fd, predetermined_input) | do_it(session, mode, experiments=None, automatic=None, cities=None, info='') | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.signals, ikabot.helpers.varios, json, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Attaquer les barbares | `ikabot/function/attackBarbarians.py` | attackBarbarians(session, event, stdin_fd, predetermined_input) | do_it(session, island, city, babarians_info, plan, ship_capacity) | decimal, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, json, math, re, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Automatiser les attaques barbares | `ikabot/function/autoBarbarians.py` | autoBarbarians(session, event, stdin_fd, predetermined_input) | do_it(session, island, city, float_city, schematic, units_data, ship_capacity, send_notifications=True) | collections, decimal, ikabot.config, ikabot.function.activateMiracle, ikabot.function.attackBarbarians, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, math, re, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Rechercher des emplacements libres | `ikabot/function/searchForIslandSpaces.py` | searchForIslandSpaces(session, event, stdin_fd, predetermined_input) | do_it(session, islandList, time, fights) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, sys, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Explorer et surveiller le monde | `ikabot/function/dumpWorld.py` | dumpWorld(session, event, stdin_fd, predetermined_input) | do_dumpWorld(session, waiting_time, coords, radius, shallow, non_empty_islands) | ast, gzip, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, json, os, pathlib, re, sys, threading, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Configurer le proxy du moteur | `ikabot/function/proxyConf.py` | proxyConf(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, requests, sys | Remplacé par le proxy strict du profil, couvrant aussi le lobby. |
| Arrêter les tâches du moteur | `ikabot/function/killTasks.py` | killTasks(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | datetime, ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, sys | Remplacé par l'arrêt des processus Desktop, isolés par profil. |
| Configurer la résolution des captchas | `ikabot/function/decaptchaConf.py` | decaptchaConf(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | base64, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, requests, sys, time | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Configurer les journaux du moteur | `ikabot/function/logs.py` | logs(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, logging, sys | Remplacé par l'historique Desktop sans journal réseau brut. |
| Importer ou exporter des cookies | `ikabot/function/importExportCookie.py` | importExportCookie(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | datetime, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, json, requests, sys, time, urllib.parse | À intégrer : transfert de secrets à protéger, jamais en clair. |
| Charger un module personnalisé | `ikabot/function/loadCustomModule.py` | loadCustomModule(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, importlib.machinery, os, sys, traceback | À intégrer : exécution de code arbitraire incompatible avec les garanties réseau actuelles. |
| Outils développeur du moteur | `ikabot/function/developer.py` | developer(session, event, stdin_fd, *args) | Configuration / action immédiate | ikabot, ikabot.helpers.decorators, ikabot.helpers.dns, os, sys | À intégrer : sorties susceptibles d'exposer des secrets. |
| Tester Telegram | `ikabot/function/testTelegramBot.py` | testTelegramBot(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, sys | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Tester Discord | `ikabot/function/testDiscordBot.py` | testDiscordBot(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.gui, ikabot.helpers.pedirInfo, sys | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Regrouper les ressources | `ikabot/function/consolidateResources.py` | consolidateResources(session, event, stdin_fd, predetermined_input) | do_it(session, limits, sourceCityIds, destinationCityId, intervalInHours, shipType=SHIP_TYPE_TRADE_SHIPS) | datetime, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.resources, ikabot.helpers.signals, ikabot.helpers.varios, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Planifier les transports de ressources | `ikabot/function/resourceTransportManager.py` | resourceTransportManager(session, event, stdin_fd, predetermined_input) | do_it_unified(session, mode, info='', origin_cities=None, destination_city=None, island=None, interval_hours=None, resource_config=None, useFreighters=None, send_mode=None, telegram_enabled=None, notify_on_start=None, origin_city=None, destination_cities=None) | datetime, ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.naval, ikabot.helpers.pedirInfo, ikabot.helpers.planRoutes, ikabot.helpers.signals, ikabot.helpers.varios, json, os, re, time, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Affecter les ouvriers | `ikabot/function/modifyProduction.py` | modifyProduction(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.pedirInfo, ikabot.helpers.varios | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Affecter les chercheurs | `ikabot/function/modifyProduction.py` | modifyAcademyWorkers(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.pedirInfo, ikabot.helpers.varios | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Gérer les tavernes | `ikabot/function/tavernManager.py` | tavernManager(session, event, stdin_fd, predetermined_input) | do_tavernManager(session, run_hours, cities_ids, cities, notification_mode) | ikabot.config, ikabot.helpers.botComm, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, ikabot.helpers.process, ikabot.helpers.signals, ikabot.helpers.varios, json, re, sys, traceback | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Affecter les prêtres | `ikabot/function/modifyProduction.py` | modifyTempleWorkers(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | ikabot.config, ikabot.helpers.decorators, ikabot.helpers.pedirInfo, ikabot.helpers.varios | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Réorganiser les bâtiments | `ikabot/function/reorganizeCityBuildings.py` | reorganizeCityBuildings(session, event, stdin_fd, predetermined_input) | Configuration / action immédiate | collections, ikabot.config, ikabot.helpers.decorators, ikabot.helpers.getJson, ikabot.helpers.gui, ikabot.helpers.pedirInfo, random, time | Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle. |
| Configurer Telegram | `ikabot/helpers/botComm.py` | updateTelegramData(session, event=None, stdin_fd=None, predetermined_input=[]) | Configuration / action immédiate | Voir le module source | Remplacé par le formulaire natif de notification avec stockage protégé ; test d'envoi distinct. |
| Configurer Discord | `ikabot/helpers/botComm.py` | updateDiscordData(session, event=None, stdin_fd=None, predetermined_input=[]) | Configuration / action immédiate | Voir le module source | Remplacé par le formulaire natif de notification avec stockage protégé ; test d'envoi distinct. |

## Inventaire exhaustif des fonctions des modules métier

Chaque définition de premier niveau est listée ci-dessous, y compris les helpers internes qui ne sont pas des commandes indépendantes. Les fonctions internes sont réutilisées par les assistants de leur module. Le fichier `INVENTAIRE.json` contient également documentation, imports et contraintes des invites.

| Source | Signature | Rôle |
|---|---|---|
| `ikabot/function/UpgradeUnits.py:20` | `getActionRequestFromHTML(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:26` | `getWorkshopTab(session, city_id, position, action_request, tab)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:40` | `send_upgrade_request(session, city_id, position, unit_id, upgrade_type, action_request, tab)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:103` | `wait_for_upgrade_completion(session, city_id, position, tab)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:144` | `wait_for_upgrade_start(session, city_id, position, tab)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:167` | `run_city_upgrades(session, city_id, city_name, position, tab, tasks)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/UpgradeUnits.py:200` | `execute_sequential_upgrades(session, jobs)` | task('UpgradeUnits') |
| `ikabot/function/UpgradeUnits.py:217` | `UpgradeUnits(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/UpgradeUnits.py:286` | `run_workshop_upgrade_interface(session, city_id, city_name, position, action_request, workshop_level=0)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:34` | `wonder_letters(name)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:48` | `assign_shortcut_letters(islands)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:73` | `find_temple_position(city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:90` | `get_temple_info(session, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:142` | `obtainMiraclesAvailable(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:206` | `activateMiracleHttpCall(session, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:232` | `chooseIsland(islands)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:272` | `wait_for_miracle(session, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:319` | `refresh_best_city(session, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateMiracle.py:352` | `do_it(session, island, iterations)` | task('activateMiracle') |
| `ikabot/function/activateMiracle.py:388` | `activateMiracle(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/activateShrine.py:18` | `findShrine(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateShrine.py:43` | `gods(godid)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateShrine.py:61` | `getFavor(session, cityid, pos)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateShrine.py:83` | `donateShrine(session, godid, cityid, pos, selected_gods)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/activateShrine.py:103` | `do_it(session, godids, mode, times, selected_gods, wait_time)` | task('activateShrine') |
| `ikabot/function/activateShrine.py:173` | `activateShrine(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/alertAttacks.py:16` | `respondToAttack(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/alertAttacks.py:53` | `do_it(session, minutes)` | task('alertAttacks') |
| `ikabot/function/alertAttacks.py:130` | `alertAttacks(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/alertLowWine.py:24` | `getMovementsFromHtml(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/alertLowWine.py:45` | `isWineTransportInProgress(session, destinationCityId)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/alertLowWine.py:77` | `do_it(session, hours, auto_transfer, transfer_amount)` | task('alertLowWine') |
| `ikabot/function/alertLowWine.py:205` | `alertLowWine(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/attackBarbarians.py:27` | `parse_game_int(text)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:34` | `choose_island(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:84` | `get_barbarians_lv(session, island, ship_capacity)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:135` | `get_units(session, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:169` | `plan_attack(session, city, babarians_info)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:270` | `get_unit_data(session, city_id, unit_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:304` | `city_is_in_island(city, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:308` | `get_barbarians_info(session, island_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:322` | `wait_until_can_attack(session, city, island, travel_time=0)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:357` | `get_movements(session, city_id=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:378` | `get_current_attacks(session, city_id, island_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:398` | `wait_for_arrival(session, city, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:413` | `wait_for_round(session, city, island, travel_time, battle_start, round_number)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:430` | `calc_travel_time(city, island, speed)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:442` | `filter_loading(attacks)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:446` | `filter_traveling(attacks, onlyCanAbort=True)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:454` | `filter_fighting(attacks)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:462` | `wait_until_attack_is_over(session, city, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:482` | `load_troops(session, city, island, attack_round, units_data, attack_data, ship_capacity, extra_cargo=0)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:509` | `loot(session, island, city, units_data, loot_round, ship_capacity)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/attackBarbarians.py:584` | `do_it(session, island, city, babarians_info, plan, ship_capacity)` | task('attackBarbarians') |
| `ikabot/function/attackBarbarians.py:671` | `attackBarbarians(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/autoBarbarians.py:156` | `choose_island(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:206` | `is_hephaestus_max(islands)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:213` | `choose_schematic()` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:225` | `check_need_float_city(schematic)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:236` | `choose_float_city(session, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:278` | `get_max_schematics_units(schematic)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:306` | `get_schematic_information(session, city, schematic, ship_capacity, float_city=None, is_in_island=False)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:354` | `print_grid_units(schematic_units, city_units, schematic_ships, ships_available)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:393` | `get_barbarians_attack_plan(barbarians_info, schematic)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:415` | `get_amount_ships_schematic(schematic_units, units_data, ship_capacity)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:426` | `has_units_in_city(session, city, units)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:445` | `do_it(session, island, city, float_city, schematic, units_data, ship_capacity, send_notifications=True)` | task('autoBarbarians') |
| `ikabot/function/autoBarbarians.py:566` | `do_attack(session, island, city, schematic, ship_capacity, float_city=None, units_data={})` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:667` | `split_wave_sends_for_group(wave_id, wave_data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:687` | `loot(session, island, city, schematic, ship_capacity, float_city=None, units_data={})` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:747` | `get_send_attack_data(session, island, city, attack_round, units_data, ship_capacity)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:786` | `get_units_scattered(session, city_id=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:808` | `extract_scattered_units(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:842` | `wait_next_scatter(session, travel_time, city_id=None, old_scatter=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:866` | `get_current_looting(session, city_id, island_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:885` | `wait_for_looting(session, city, island)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoBarbarians.py:901` | `autoBarbarians(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/autoPirate.py:38` | `isHourInRange(hour, start, end)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:45` | `getScheduledMission(dayStart, dayEnd, nightStart, nightEnd, dayChoice, nightChoice)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:55` | `getSecondsUntilNextRange(dayStart, nightStart)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:61` | `extract_captcha_image(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:98` | `do_pirate_missions(session, pirateCount, pirateSchedule, pirateMissionChoice, pirateMissionDayChoice, pirateMissionNightChoice, dayStart, dayEnd, nightStart, nightEnd, autoConvert, convertPerMission, maxRandomWaitingTime, piracyCities)` | task('autoPirate') |
| `ikabot/function/autoPirate.py:240` | `autoPirate(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/autoPirate.py:388` | `_is_png_bytes(image)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:404` | `resolveCaptcha(session, picture)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:470` | `getPiracyCityById(session, city_id, pirateMissionChoice)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:494` | `getPiracyCities(session, pirateMissionChoice)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:513` | `getPirateFortressHtml(session, cityId)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:539` | `getPirateFortressPoints(session, cityId)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:563` | `convertCapturePoints(session, piracyCities, convertPerMission)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/autoPirate.py:595` | `getCurrentMissionWaitingTime(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:30` | `chooseResource(session, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:66` | `getOffers(session, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:117` | `calculateCost(offers, total_amount_to_buy)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:137` | `chooseCommertialCity(commercial_cities)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:154` | `filterOffers(offers)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:192` | `buy(session, city, offer, amount_to_buy, ships_available, ship_capacity)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/buyResources.py:265` | `do_it(session, city, offers, amount_to_buy)` | task('buyResources') |
| `ikabot/function/buyResources.py:295` | `buyResources(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/checkForUpdate.py:10` | `checkForUpdate()` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/consolidateResources.py:31` | `do_it(session, limits, sourceCityIds, destinationCityId, intervalInHours, shipType=SHIP_TYPE_TRADE_SHIPS)` | task('consolidateResources') |
| `ikabot/function/consolidateResources.py:128` | `consolidateResources(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/constructBuilding.py:15` | `parseBuildingCosts(html_block)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructBuilding.py:40` | `splitBuildingBlocks(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructBuilding.py:49` | `constructBuilding(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/constructionList.py:33` | `_parseConstructionTime(row)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:53` | `_formatRemainingTime(seconds)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:62` | `_findHtml(value, element_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:78` | `_getFreeSpeedupParams(response, city_id, position)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:129` | `tryFreeBuildingSpeedup(session, city_id, building)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:155` | `waitForConstruction(session, city_id, final_lvl, construction_queue=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:224` | `expandBuilding(session, cityId, building, waitForResources, construction_queue=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:302` | `getCostsReducers(city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:332` | `getResourcesNeeded(session, city, building, current_level, final_level, simulated_reducers=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:505` | `_round_up_resources(amount)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:514` | `sendResourcesNeeded(session, destination_city_id, city_origins, missing_resources, useFreighters=False, useRounding=False)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:569` | `chooseResourceProviders(session, cities_ids, cities, city_id, resource, missing)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:643` | `sendResourcesMenu(session, city_id, missing)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:685` | `getBuildingsToExpand(session, cityId)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/constructionList.py:751` | `checkhash(url)` | cache |
| `ikabot/function/constructionList.py:772` | `do_it(session, city_id, city_name, buildings, shipments, expand_overall, wait_resources, construction_queue, total_time)` | task('constructionList') |
| `ikabot/function/constructionList.py:815` | `constructionList(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/decaptchaConf.py:37` | `decaptchaConf(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/decaptchaConf.py:235` | `testCustomDecaptcha(ground_truth, picture, address)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/developer.py:9` | `developer(session, event, stdin_fd, *args)` | configurator |
| `ikabot/function/distributeResources.py:20` | `do_it(session, routes, useFreighters, resource)` | task('distributeResources') |
| `ikabot/function/distributeResources.py:35` | `distributeResources(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/distributeResources.py:113` | `distribute_evenly(session, resource_type, cities_ids, cities)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/distributeResources.py:243` | `distribute_unevenly(session, resource_type, cities_ids, cities)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/donate.py:17` | `donate(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/donationBot.py:18` | `_get_donation_config(cities, donate_method, cityId)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/donationBot.py:93` | `do_it(session, cities_ids, cities_dict, waiting_time, donate_method)` | task('donationBot') |
| `ikabot/function/donationBot.py:215` | `donationBot(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/dumpWorld.py:29` | `do_dumpWorld(session, waiting_time, coords, radius, shallow, non_empty_islands)` | task('dumpWorld') |
| `ikabot/function/dumpWorld.py:62` | `dumpWorld(session, event, stdin_fd, predetermined_input)` | configurator(blocking=True) |
| `ikabot/function/dumpWorld.py:131` | `do_it(session, waiting_time, coords, radius, shallow, non_empty_islands, shared_data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:318` | `dump(world, dump_path, dump_name)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:327` | `dump_islands(shared_data, all_island, waiting_time, session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:353` | `update_terminal(shared_data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:378` | `update_status(message, percent, percent_total, shared_data, add_history=False)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:393` | `view_dump(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:671` | `print_map(islands, selected_islands)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:719` | `filter_on_condition(island, condition)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:756` | `convert_to_shallow(islands)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:786` | `unique_tuples(tuples)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/dumpWorld.py:795` | `get_files(path)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:39` | `getCacheFile(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:56` | `parseCityProduction(html, typeGood)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:96` | `formatBuildingLevel(level, isBusy)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:106` | `displayBuildingTable(city_names, ids, city_buildings)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:201` | `displayBuildingList(city_names, ids, city_buildings, city_tradegoods)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:230` | `showCityDetail(city, city_header, wood_prod, good_prod, color_arr)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:326` | `displayAccountSummary(data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:371` | `saveCache(session, data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:387` | `loadCache(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:406` | `collectData(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/getStatus.py:521` | `getStatus(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/importExportCookie.py:19` | `wait_for_key_or_timeout(key, timeout_seconds)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/importExportCookie.py:67` | `importExportCookie(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/importExportCookie.py:94` | `_redirectedToLobby(response)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/importExportCookie.py:105` | `_clearIkariamCookies(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/importExportCookie.py:110` | `importCookie(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/importExportCookie.py:177` | `exportCookie(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/importExportCookie.py:211` | `sendCookieToTelegram(session, cookies_js)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/killTasks.py:14` | `killTasks(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/loadCustomModule.py:14` | `loadCustomModule(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/loginDaily.py:19` | `is_collectable(row)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:35` | `collect_resource_favour(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:57` | `look(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:111` | `capture_runs(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:116` | `donate_wood(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:121` | `stay_online_30_mins(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:137` | `complete_tasks(session, table, wine_city, earliest_wakeup_time)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/loginDaily.py:158` | `do_it(session, wine_city, wood_city, luxury_city, favour_tasks, collect_ambrosia)` | task('loginDaily') |
| `ikabot/function/loginDaily.py:429` | `loginDaily(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/logs.py:14` | `logs(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/logs.py:68` | `viewLogs()` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/modifyProduction.py:10` | `modifyProduction(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/modifyProduction.py:127` | `modifyAcademyWorkers(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/modifyProduction.py:187` | `modifyTempleWorkers(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/proxyConf.py:14` | `show_proxy(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/proxyConf.py:42` | `test_proxy(session, proxy_dict)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/proxyConf.py:56` | `read_proxy(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/proxyConf.py:82` | `proxyConf(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/reorganizeCityBuildings.py:19` | `_normalize(building)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/reorganizeCityBuildings.py:23` | `_compute_moves(template_city, target_city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/reorganizeCityBuildings.py:87` | `reorganizeCityBuildings(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/research.py:18` | `get_studies(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/research.py:30` | `study(session, studies, num_study)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/research.py:43` | `experiment(session, experiments, automatic)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/research.py:100` | `find_academy_cities(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/research.py:117` | `experiment_multi(session, cities)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/research.py:199` | `do_it(session, mode, experiments=None, automatic=None, cities=None, info='')` | task('research') |
| `ikabot/function/research.py:207` | `research(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/resourceTransportManager.py:23` | `print_module_banner(page_title=None)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:43` | `get_lock_file_path(session, use_freighters=False)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:73` | `acquire_shipping_lock(session, use_freighters=False, timeout=300)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:133` | `release_shipping_lock(session, use_freighters=False)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:159` | `readResourceAmount(resource_name)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:203` | `do_it_unified(session, mode, info='', origin_cities=None, destination_city=None, island=None, interval_hours=None, resource_config=None, useFreighters=None, send_mode=None, telegram_enabled=None, notify_on_start=None, origin_city=None, destination_cities=None)` | task('resourceTransportManager') |
| `ikabot/function/resourceTransportManager.py:211` | `resourceTransportManager(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/resourceTransportManager.py:242` | `consolidateMode(session, telegram_enabled)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:708` | `distributeMode(session, telegram_enabled)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:904` | `do_it(session, origin_cities, destination_city, island, interval_hours, resource_config, useFreighters, send_mode, telegram_enabled, notify_on_start)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/resourceTransportManager.py:1143` | `do_it_distribute(session, origin_city, destination_cities, interval_hours, resource_config, useFreighters, telegram_enabled, notify_on_start)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/searchForIslandSpaces.py:19` | `do_it(session, islandList, time, fights)` | task('searchForIslandSpaces') |
| `ikabot/function/searchForIslandSpaces.py:139` | `searchForIslandSpaces(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/sellResources.py:23` | `chooseCommercialCity(commercial_cities)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:40` | `getMarketInfo(session, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:67` | `getOffers(session, my_market_city, resource_type)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:125` | `sellToOffers(session, city_to_buy_from, resource_type)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:213` | `createOffer(session, my_offering_market_city, resource_type)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:271` | `do_it(session, mode, amount_to_sell=None, offers=None, resource_type=None, city_to_buy_from=None, price=None, sell_market_capacity=None, city=None)` | task('sellResources') |
| `ikabot/function/sellResources.py:290` | `sellResources(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/sellResources.py:320` | `do_it1(session, left_to_sell, offers, resource_type, city_to_buy_from)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sellResources.py:391` | `do_it2(session, amount_to_sell, price, resource_type, sell_market_capacity, city)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/sendResources.py:19` | `do_it(session, routes, useFreighters)` | task('sendResources') |
| `ikabot/function/sendResources.py:33` | `sendResources(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/shipMovements.py:20` | `isHostile(movement)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/shipMovements.py:39` | `shipMovements(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/stationArmy.py:10` | `getCityMilitaryData(session, city_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/stationArmy.py:36` | `extractTooltipsAndValues(data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/stationArmy.py:42` | `calculateTotals(tooltips, values)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/stationArmy.py:64` | `getArmyAvailable(session, type_army, destination_city_id, origin_city_id, event)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/stationArmy.py:118` | `sendArmy(session, origin_city, destination_city, type_army, army_available)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/stationArmy.py:139` | `stationArmy(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/tavernManager.py:379` | `_print_results_table(results)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/tavernManager.py:418` | `do_tavernManager(session, run_hours, cities_ids, cities, notification_mode)` | task('tavernManager') |
| `ikabot/function/tavernManager.py:434` | `tavernManager(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/tavernManager.py:470` | `_run_set_mode(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/tavernManager.py:524` | `_run_equilibrium_mode(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/testDiscordBot.py:12` | `testDiscordBot(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/testTelegramBot.py:12` | `testTelegramBot(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/trainArmy.py:22` | `getBuildingInfo(session, city, trainTroops)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/trainArmy.py:48` | `train(session, city, trainings, trainTroops)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/trainArmy.py:75` | `waitForTraining(session, city, trainTroops)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/trainArmy.py:92` | `planTrainings(session, city, trainings, trainTroops)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/trainArmy.py:165` | `generateArmyData(units_info)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/trainArmy.py:188` | `do_trainArmy(session, city, tranings, trainTroops, replicate, countRepeat, cityTrainings, units)` | task('trainArmy') |
| `ikabot/function/trainArmy.py:231` | `trainArmy(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/trainArmy.py:468` | `filterCitiesByResource(cities, resource_id, cityTrainings)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/update.py:14` | `update(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/vacationMode.py:13` | `activateVacationMode(session)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/vacationMode.py:34` | `vacationMode(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/viewArmy.py:13` | `getCityMilitaryData(session, city_id)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/viewArmy.py:29` | `extractTooltipsAndValues(data)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/viewArmy.py:35` | `parseUnits(html)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/viewArmy.py:55` | `displayTable(city_names, ids, city_ground, city_ships, cities, show_ships)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/viewArmy.py:100` | `displaySections(city_names, ids, city_ground, city_ships, cities, show_ships)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/viewArmy.py:141` | `viewArmy(session, event, stdin_fd, predetermined_input)` | configurator |
| `ikabot/function/webServer.py:45` | `get_local_network_ip()` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/webServer.py:70` | `get_request_params(request)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/webServer.py:95` | `do_webServer(session, port, local_network_ip)` | task('webServer') |
| `ikabot/function/webServer.py:292` | `webServer(session, event, stdin_fd, predetermined_input, port=None)` | configurator |
| `ikabot/function/webServer.py:413` | `handleIkabotAPIRequest(session, request)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/webServer.py:427` | `mayorMessageResponse(type: ResponseTypes, message: str)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/webServer.py:431` | `addSandbox(session, resp, req)` | Helper interne / appelé par les fonctions du module |
| `ikabot/function/webServer.py:483` | `generateTableHTML(process_list)` | Helper interne / appelé par les fonctions du module |

## Redistribution

Le dépôt est sous licence MIT, copyright 2018 Physics ; conserver LICENSE. PySide6/Qt est disponible notamment sous LGPLv3/GPLv3/commercial : cette distribution utilise les bibliothèques dynamiques Qt dans un dossier PyInstaller onedir, sans UPX. Conserver les notices et permettre le remplacement des bibliothèques LGPL et le débogage de leurs modifications. Consulter `LICENCES.md` avant redistribution publique : les notices des dépendances et la provenance des poids binaires doivent être vérifiées. Aucun droit d'utilisation du service de jeu n'est accordé par la licence du code.

## Limites vérifiées et travail restant

- Pas d'exécutable Windows compilé ou testé dans cet environnement Linux ; scripts et workflow Windows fournis.
- Pas de connexion réelle, ni d'action en jeu exécutée. Les tests de données simulées ne remplacent pas ces essais.
- Pas encore de traduction exhaustive des textes internes et des noms de bâtiments inconnus.
- Une opération simultanée par profil ; aucune reprise automatique des actions interrompues.
- Les mises à jour, exports de cookies, modules personnalisés, outils développeur et serveur web ne sont pas exposés.
- L'authentification du proxy n'est pas prise en charge ; HTTP(S) et SOCKS5h sans identifiants seulement.
- Les requêtes non HTTPS sont bloquées. Une API découverte uniquement en HTTP nécessite une adresse HTTPS fiable ou le parcours manuel du moteur.
- Le blocage proxy est un garde-fou du processus, pas un pare-feu Windows. Les essais réels Windows, VPN, IPv6 et proxy SOCKS restent nécessaires.
- Les mouvements sont projetés dans le tableau de bord avec le chemin JSON du moteur ; leur validation sur un compte réel reste à faire.
