"""Traductions de l'enveloppe et des invites courantes du moteur.

Le moteur ne fournit pas de catalogue français : les textes non traduits restent
visibles, identifiés comme tels, pour éviter de masquer une instruction.
"""
WORDS = {
    "Mail:": "Adresse e-mail :", "Mail: ": "Adresse e-mail :",
    "Password:": "Mot de passe :", "Password: ": "Mot de passe :",
    "[Enter]": "Continuer", "Invalid option": "Choix invalide",
    "Origin city:": "Ville de départ :", "Destination city": "Ville de destination",
    "What type of ships do you want to use? (Default: Trade ships)": "Type de navires (par défaut : navires marchands)",
    "(1) Trade ships": "(1) Navires marchands", "(2) Freighters": "(2) Cargos",
    "There are no movements": "Aucun mouvement en cours",
    "Obtaining new blackbox token, please wait...": "Obtention du jeton de connexion…",
    "wood": "Bois", "wine": "Vin", "marble": "Marbre", "crystal": "Cristal", "sulfur": "Soufre",
    "townHall": "Hôtel de ville", "academy": "Académie", "warehouse": "Entrepôt",
    "tavern": "Taverne", "palace": "Palais", "palaceColony": "Résidence du gouverneur",
    "port": "Port commercial", "shipyard": "Chantier naval", "barracks": "Caserne",
    "wall": "Mur d'enceinte", "museum": "Musée", "temple": "Temple", "embassy": "Ambassade",
    "branchOffice": "Comptoir", "workshop": "Atelier", "safehouse": "Cachette",
    "pirateFortress": "Forteresse pirate", "dump": "Dépôt", "shrine": "Sanctuaire",
    "carpentering": "Menuiserie", "architect": "Bureau de l'architecte",
    "optician": "Opticien", "fireworker": "Atelier d'artificier", "vineyard": "Pressoir à vin",
    "forester": "Maison forestière", "stonemason": "Tailleur de pierre", "glassblowing": "Souffleur de verre",
    "winegrower": "Viticulteur", "alchemist": "Tour de l'alchimiste", "blackMarket": "Marché noir",
    "seaChartArchive": "Archives des cartes marines", "dockyard": "Bassin de radoub",
    "ChronosForge": "Forge de Chronos", "godShrine": "Sanctuaire des dieux",
}


def tr(text):
    return "\n".join(WORDS.get(line.strip(), line) for line in str(text).splitlines())
