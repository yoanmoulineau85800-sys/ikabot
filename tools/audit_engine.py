"""Inventaire reproductible du code réellement présent, sans importer le moteur."""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktop.catalog import ACTIONS


def signature(node):
    return node.name + "(" + ast.unparse(node.args) + ")"


def main():
    modules, functions = {}, []
    for path in sorted((ROOT / "ikabot" / "function").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = sorted({node.module or "" for node in tree.body if isinstance(node, ast.ImportFrom)} |
                         {alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names})
        entries = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = [ast.unparse(d) for d in node.decorator_list]
            prompts = [{kw.arg: ast.unparse(kw.value) for kw in call.keywords}
                       for call in ast.walk(node) if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "read"]
            item = {"source": str(path.relative_to(ROOT)), "line": node.lineno,
                    "signature": signature(node), "decorators": decorators,
                    "doc": ast.get_docstring(node) or "", "prompts": prompts, "imports": imports}
            entries.append(item)
            functions.append(item)
        modules["ikabot.function." + path.stem] = entries
    output = ["# Audit Ikabot Desktop", "", "Source officielle : https://github.com/Ikabot-Collective/ikabot",
              "Commit analysé : `c300e506458007c1812a2225abea0db41c096d6f` (moteur 7.7.2).",
              "Le checkout original /workspace/ikabot est conservé. Le développement utilise une copie indépendante et la branche desktop/francais.",
              "", "## Architecture constatée", "",
              "`command_line.py` sélectionne les fonctions ; `web/session.py` gère Gameforge, lobby, comptes, cookies, renouvellement et requêtes Ikariam. "
              "`helpers/sessionStorage.py` gère les fichiers de sessions ; `helpers/decorators.py` sépare les configurateurs interactifs et les tâches ; "
              "`helpers/process.py` suit les processus. `pedirInfo.py` valide les choix et découvre les villes ; `getJson.py` analyse les réponses. "
              "Les helpers naval/resources/planRoutes réutilisent les mêmes sessions. Les captchas locaux utilisent des poids binaires et éventuellement multiprocessing. "
              "`apiComm.py`, `dns.py` et `botComm.py` utilisent aussi requests en dehors de Session.",
              "", "## Entrées fonctionnelles et statut", "",
              "Les paramètres des configurateurs sont principalement session, event, stdin_fd, predetermined_input. "
              "Les paramètres métier sont obtenus par leurs assistants : le JSON joint inventorie chaque appel read et ses contraintes, sans inventer de formulaire statique. "
              "Leur retour dict est transmis à la tâche d'origine. « Assistant » signifie raccordé au code, contrat testé et formulaires réels ; "
              "cela ne signifie pas validation en jeu. Sans compte de test, tous les parcours réseau métier restent à valider.", "",
              "| Fonction | Module source | Paramètres du configurateur | Paramètres de tâche | Dépendances | Faisabilité / statut |",
              "|---|---|---|---|---|---|"]
    for action in ACTIONS.values():
        entries = modules.get(action.module, [])
        entry = next((e for e in entries if e["signature"].startswith(action.function + "(")), None)
        tasks = [e["signature"] for e in entries if any(d.startswith("task(") and repr(action.function) in d for d in e["decorators"])]
        source = (action.module.replace(".", "/") + ".py")
        deps = ", ".join((entry or {}).get("imports", []))
        status = action.reason or "Assistant Qt raccordé ; essai réel en jeu non exécuté. Traduction partielle."
        output.append("| " + " | ".join([action.label, f"`{source}`", (entry or {}).get("signature", action.function + "(session, event=None, stdin_fd=None, predetermined_input=[])"), "; ".join(tasks) or "Configuration / action immédiate", deps or "Voir le module source", status]) + " |")
    output += ["", "## Inventaire exhaustif des fonctions des modules métier", "",
               "Chaque définition de premier niveau est listée ci-dessous, y compris les helpers internes qui ne sont pas des commandes indépendantes. "
               "Les fonctions internes sont réutilisées par les assistants de leur module. Le fichier `INVENTAIRE.json` contient également documentation, imports et contraintes des invites.",
               "", "| Source | Signature | Rôle |", "|---|---|---|"]
    for item in functions:
        role = " / ".join(item["decorators"]) or "Helper interne / appelé par les fonctions du module"
        output.append(f'| `{item["source"]}:{item["line"]}` | `{item["signature"]}` | {role} |')
    output += ["", "## Redistribution", "",
               "Le dépôt est sous licence MIT, copyright 2018 Physics ; conserver LICENSE. PySide6/Qt est disponible notamment sous LGPLv3/GPLv3/commercial : "
               "cette distribution utilise les bibliothèques dynamiques Qt dans un dossier PyInstaller onedir, sans UPX. "
               "Conserver les notices et permettre le remplacement des bibliothèques LGPL et le débogage de leurs modifications. "
               "Consulter `LICENCES.md` avant redistribution publique : les notices des dépendances et la provenance des poids binaires doivent être vérifiées. "
               "Aucun droit d'utilisation du service de jeu n'est accordé par la licence du code.",
               "", "## Limites vérifiées et travail restant", "",
               "- Pas d'exécutable Windows compilé ou testé dans cet environnement Linux ; scripts et workflow Windows fournis.",
               "- Pas de connexion réelle, ni d'action en jeu exécutée. Les tests de données simulées ne remplacent pas ces essais.",
               "- Pas encore de traduction exhaustive des textes internes et des noms de bâtiments inconnus.",
               "- Une opération simultanée par profil ; aucune reprise automatique des actions interrompues.",
               "- Les mises à jour, exports de cookies, modules personnalisés, outils développeur et serveur web ne sont pas exposés.",
               "- L'authentification du proxy n'est pas prise en charge ; HTTP(S) et SOCKS5h sans identifiants seulement.",
               "- Les requêtes non HTTPS sont bloquées. Une API découverte uniquement en HTTP nécessite une adresse HTTPS fiable ou le parcours manuel du moteur.",
               "- Le blocage proxy est un garde-fou du processus, pas un pare-feu Windows. Les essais réels Windows, VPN, IPv6 et proxy SOCKS restent nécessaires.",
               "- Les mouvements sont projetés dans le tableau de bord avec le chemin JSON du moteur ; leur validation sur un compte réel reste à faire."]
    (ROOT / "docs" / "AUDIT.md").write_text("\n".join(output) + "\n", encoding="utf-8")
    (ROOT / "docs" / "INVENTAIRE.json").write_text(json.dumps(functions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(ACTIONS)} entrées cataloguées, {len(functions)} fonctions inventoriées.")


if __name__ == "__main__":
    main()
