"""Catalogue explicite des points d'entrée vérifiés dans le moteur."""
from dataclasses import dataclass

SECTIONS = ["Tableau de bord", "Comptes et profils", "Villes", "Ressources",
            "Bâtiments et constructions", "Recherches", "Transports", "Armées et flottes",
            "Missions et automatisations", "Alertes et notifications", "Historique et journaux",
            "Réseau et connexions", "Paramètres"]


@dataclass(frozen=True)
class Action:
    module: str
    function: str
    label: str
    section: str
    reason: str = ""


_ROWS = [
    ("constructionList", "File de construction", 4),
    ("sendResources", "Envoyer des ressources", 6),
    ("distributeResources", "Répartir les ressources", 3),
    ("getStatus", "État du compte", 0, "Remplacé par le tableau de bord natif."),
    ("activateShrine", "Activer le sanctuaire", 8),
    ("loginDaily", "Connexion quotidienne", 8),
    ("alertAttacks", "Surveiller les attaques", 9),
    ("alertLowWine", "Surveiller les réserves de vin", 9),
    ("buyResources", "Acheter des ressources", 3),
    ("sellResources", "Vendre des ressources", 3),
    ("donate", "Faire un don", 3),
    ("donationBot", "Automatiser les dons", 8),
    ("vacationMode", "Activer le mode vacances", 8),
    ("activateMiracle", "Activer un miracle", 8),
    ("trainArmy", "Recruter des troupes et des navires", 7),
    ("stationArmy", "Déplacer les troupes et les navires", 7),
    ("UpgradeUnits", "Améliorer les unités", 7),
    ("viewArmy", "Consulter les armées", 7),
    ("shipMovements", "Consulter les mouvements", 6),
    ("constructBuilding", "Construire ou améliorer un bâtiment", 4),
    ("update", "Mettre à jour le moteur", 12, "La mise à jour se fait par remplacement de la distribution complète."),
    ("webServer", "Serveur web du moteur", 12, "À intégrer : serveur lié à la session, exposition et arrêt à sécuriser."),
    ("autoPirate", "Automatiser la piraterie", 8),
    ("research", "Effectuer une recherche", 5),
    ("attackBarbarians", "Attaquer les barbares", 7),
    ("autoBarbarians", "Automatiser les attaques barbares", 8),
    ("searchForIslandSpaces", "Rechercher des emplacements libres", 2),
    ("dumpWorld", "Explorer et surveiller le monde", 2),
    ("proxyConf", "Configurer le proxy du moteur", 11, "Remplacé par le proxy strict du profil, couvrant aussi le lobby."),
    ("killTasks", "Arrêter les tâches du moteur", 8, "Remplacé par l'arrêt des processus Desktop, isolés par profil."),
    ("decaptchaConf", "Configurer la résolution des captchas", 12),
    ("logs", "Configurer les journaux du moteur", 10, "Remplacé par l'historique Desktop sans journal réseau brut."),
    ("importExportCookie", "Importer ou exporter des cookies", 1, "À intégrer : transfert de secrets à protéger, jamais en clair."),
    ("loadCustomModule", "Charger un module personnalisé", 12, "À intégrer : exécution de code arbitraire incompatible avec les garanties réseau actuelles."),
    ("developer", "Outils développeur du moteur", 12, "À intégrer : sorties susceptibles d'exposer des secrets."),
    ("testTelegramBot", "Tester Telegram", 9),
    ("testDiscordBot", "Tester Discord", 9),
    ("consolidateResources", "Regrouper les ressources", 3),
    ("resourceTransportManager", "Planifier les transports de ressources", 6),
    ("modifyProduction", "Affecter les ouvriers", 3),
    ("modifyAcademyWorkers", "Affecter les chercheurs", 5),
    ("tavernManager", "Gérer les tavernes", 3),
    ("modifyTempleWorkers", "Affecter les prêtres", 8),
    ("reorganizeCityBuildings", "Réorganiser les bâtiments", 4),
]
ACTIONS = {}
for row in _ROWS:
    name, label, section, *reason = row
    module = "modifyProduction" if name in ("modifyAcademyWorkers", "modifyTempleWorkers") else name
    ACTIONS[name] = Action("ikabot.function." + module, name, label, SECTIONS[section], reason[0] if reason else "")
for name, label in [("updateTelegramData", "Configurer Telegram"), ("updateDiscordData", "Configurer Discord")]:
    ACTIONS[name] = Action("ikabot.helpers.botComm", name, label, SECTIONS[9],
                           "Remplacé par le formulaire natif de notification avec stockage protégé ; test d'envoi distinct.")
