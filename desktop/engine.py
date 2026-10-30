"""Adaptateur du moteur, exécuté exclusivement dans un processus de profil.

Aucun compte, mot de passe ou cookie n'est envoyé en argument de ligne de commande.
Le protocole Pipe reste local au parent et au processus qu'il crée.
"""
import builtins
import copy
import getpass
import importlib
import io
import json
import logging
import os
import re
import threading
import time
from pathlib import Path

from desktop.catalog import ACTIONS
from desktop.network import NetworkPolicy
from desktop.security import save_secret, unprotect


class Cancelled(BaseException):
    pass


class Transcript(io.TextIOBase):
    def __init__(self):
        self.parts = []
        self.callback = None
        self.last_emission = 0
        self.reported_error = False

    def write(self, value):
        if "Traceback (most recent call last)" in str(value):
            self.reported_error = True
        self.parts.append(str(value))
        if sum(map(len, self.parts)) > 24000:
            self.parts = ["".join(self.parts)[-16000:]]
        if self.callback and time.monotonic() - self.last_emission > 0.25:
            self.last_emission = time.monotonic()
            self.callback("".join(self.parts)[-12000:])
        return len(value)

    def take(self):
        text = "".join(self.parts)
        self.parts.clear()
        return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text).strip()

    def flush(self):
        pass


class SecretFilter:
    def __init__(self):
        self.values = set()

    def add(self, value):
        if value:
            self.values.add(str(value))

    def clean(self, text):
        for secret in sorted(self.values, key=len, reverse=True):
            text = text.replace(secret, "[secret masqué]")
        text = re.sub(r"(?i)((?:password|cookie|token|authorization|blackbox|sessionid)[\w-]*[\s\"':=]+)[^\s,;}]+",
                      r"\1[secret masqué]", text)
        text = re.sub(r"(https?://)[^\s/@]+:[^\s/@]+@", r"\1[secret masqué]@", text)
        return text


def install_storage(root):
    """Replace only engine storage boundaries; no legacy data is imported."""
    from ikabot.helpers import sessionStorage as storage
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    memory = {}
    storage.get_ikabot_dir = lambda: str(root)

    def read(path, default=None):
        if os.name != "nt":
            return copy.deepcopy(memory.get(str(path), default))
        path = Path(path)
        if not path.exists():
            return copy.deepcopy(default)
        return json.loads(unprotect(path.read_bytes()))

    def write(path, data):
        if os.name == "nt":
            save_secret(path, json.dumps(data, ensure_ascii=False).encode())
        else:
            memory[str(path)] = copy.deepcopy(data)

    storage.read_json_file = read
    storage.write_json_file = write
    storage.init_storage()


def snapshot(session):
    """Projection sans jetons des données réelles analysées par Ikabot."""
    from ikabot.helpers.pedirInfo import getIdsOfCities
    from ikabot.helpers.getJson import getCity
    from ikabot import config
    from ikabot.helpers import pedirInfo
    pedirInfo.ids_cache = pedirInfo.cities_cache = None
    ids, _ = getIdsOfCities(session)
    cities = []
    for city_id in ids:
        city = getCity(session.get(config.city_url + str(city_id)))
        cities.append({"id": str(city_id), "name": city["name"],
                       "resources": city["availableResources"],
                       "buildings": [{"name": p.get("building", ""), "level": p.get("level", ""),
                                      "busy": p.get("isBusy", False)} for p in city["position"]
                                     if p.get("building") not in ("", "empty")],
                       "x": city["x"], "y": city["y"]})
    result = {"cities": cities, "server": getattr(session, "urlBase", "").split("?")[0]}
    try:
        result["movements"] = snapshot_movements(session)
    except Exception as exc:
        result["movements"] = None
        result["movements_error"] = type(exc).__name__
    return result


def snapshot_movements(session):
    # Same endpoint and response path as function/shipMovements.py. Only the
    # safe display projection is duplicated, not the movement execution logic.
    from ikabot.helpers.varios import getCurrentCityId
    from ikabot.config import actionRequest
    city_id = getCurrentCityId(session)
    response = json.loads(session.post(
        f"view=militaryAdvisor&oldView=city&oldBackgroundView=city&backgroundView=city&currentCityId={city_id}&actionRequest={actionRequest}&ajax=1"))
    source = response[1][1][2]["viewScriptParams"]["militaryAndFleetMovements"]
    return [{"origin": m["origin"]["name"], "target": m["target"]["name"],
             "mission": m["event"]["missionText"], "arrival": int(m["eventTime"]),
             "hostile": bool(m["isHostile"]), "returning": bool(m["event"]["isFleetReturning"])} for m in source]


def invoke(session, action_id):
    """Reuse configurators and tasks without their CLI process decorator.

The Desktop supervisor owns lifetime, session logout and cancellation instead.
"""
    action = ACTIONS[action_id]
    if action.reason:
        raise ValueError(action.reason)
    module = importlib.import_module(action.module)
    configurator = getattr(module, action.function)
    if not getattr(configurator, "_is_configurator", False):
        raise TypeError("Contrat du moteur incompatible")
    event = threading.Event()
    result = configurator.__wrapped__(session, event, None, [])
    if result is not None:
        from ikabot.helpers.decorators import _TASK_REGISTRY
        task = _TASK_REGISTRY.get(action.function)
        if task is None:
            raise RuntimeError("Tâche du moteur absente")
        task.__wrapped__(**result)


def run_worker(connection, profile, root):
    import sys
    transcript = Transcript()
    sys.stdout = sys.stderr = transcript
    secrets = SecretFilter()
    session = None
    policy = None

    def emit(kind, **data):
        connection.send({"type": kind, **data})

    transcript.callback = lambda text: emit("progress", text=secrets.clean(text))

    def prompt(message="", secret=False, **constraints):
        if str(message).strip() == "Mail:":
            return profile["email"]
        secret = secret or not any(constraints.get(k) is not None for k in ("min", "max", "values")) and not constraints.get("digit") and not constraints.get("empty")
        emit("prompt", message=str(message), context=secrets.clean(transcript.take()),
             secret=secret, constraints=constraints)
        reply = connection.recv()
        if reply.get("command") != "answer":
            raise Cancelled()
        answer = reply.get("value", "")
        if secret:
            secrets.add(answer)
        return answer

    try:
        policy = NetworkPolicy(profile.get("proxy", "")).install()
        import ikabot.config as config
        # Suppress the engine's raw network/file log before it is initialized.
        config.LOGS_DIRECTORY_FILE = os.devnull
        config.do_ssl_verify = True
        config.IKABOT_LOCALE = "fr-FR"
        config.IKABOT_GF_LANG = "fr"
        config.IKABOT_TIMEZONE_ID = "Europe/Paris"
        config.predetermined_input = []
        install_storage(Path(root) / profile["id"] / "sessions")
        import ikabot.helpers.logging
        class SafeLogHandler(logging.Handler):
            def emit(self, record):
                if record.levelno >= logging.ERROR:
                    transcript.reported_error = True
                emit("engine_log", level=record.levelname, component=record.name)
        for handler in list(logging.getLogger().handlers):
            logging.getLogger().removeHandler(handler)
            handler.close()
        logging.getLogger().addHandler(SafeLogHandler())
        logging.getLogger().setLevel(logging.WARNING)
        logging.disable(logging.NOTSET)
        from ikabot.helpers import gui, pedirInfo, dns
        original_address = dns.getAddress
        # Patch before importing function modules (which use `from ... import`).
        gui.clear = lambda: transcript.take()
        gui.banner = lambda: None
        gui.enter = lambda: prompt("Continuer", empty=True)
        builtins.input = lambda message="": prompt(message)
        getpass.getpass = lambda message="Mot de passe", stream=None: prompt(message, secret=True)
        original_read = pedirInfo.read

        def read(*args, **kwargs):
            # Keep the engine's existing validation/conversion. Replace its input
            # only, supplying constraints so the Qt form can validate early too.
            def graphical_input(message=""):
                return prompt(message, **{k: v for k, v in kwargs.items()
                                          if k in ("min", "max", "digit", "values", "empty", "default", "additionalValues")})
            builtins.input = graphical_input
            try:
                return original_read(*args, **kwargs)
            finally:
                builtins.input = lambda message="": prompt(message)
        pedirInfo.read = read
        # Engine DNS uses UDP/subprocess fallback. Replace with HTTPS DNS through
        # the very same requests policy, including in proxy mode.
        def api_address(domain=config.publicAPIServerDomain):
            import requests
            configured = os.environ.get("CUSTOM_API_ADDRESS", "").strip()
            if configured:
                if not configured.startswith("https://"):
                    raise ValueError("L'API configurée doit utiliser HTTPS")
                return configured.rstrip("/")
            response = requests.get("https://dns.google/resolve", params={"name": domain, "type": "TXT"})
            response.raise_for_status()
            answers = response.json().get("Answer", [])
            for answer in answers:
                if answer.get("type") == 16:
                    address = answer["data"].replace('"', "").strip()
                    if not address.startswith("https://"):
                        raise ValueError("L'API découverte n'utilise pas HTTPS")
                    return address.replace("/ikagod/ikabot", "")
            raise ValueError("Adresse HTTPS de l'API introuvable")
        dns.getAddress = api_address
        # Expose only a login prompt. Credentials are supplied over the Pipe.
        from ikabot.web.session import Session
        original_status = Session.setStatus
        def set_status(s, message):
            emit("progress", text=secrets.clean(str(message)))
            original_status(s, message)
        Session.setStatus = set_status
        for module_name, module in list(sys.modules.items()):
            if module_name.startswith("ikabot.") and getattr(module, "getAddress", None) is original_address:
                module.getAddress = api_address
        emit("state", state="Connexion en cours")
        session = Session()
        from urllib.parse import urlsplit
        expected_server = profile.get("server", "").strip().lower()
        if expected_server and urlsplit(session.urlBase).hostname != expected_server:
            raise ValueError("Le serveur choisi ne correspond pas au profil")
        emit("state", state="Connecté")
        while True:
            emit("idle")
            command = connection.recv()
            kind = command.get("command")
            if kind == "quit":
                break
            try:
                transcript.reported_error = False
                if kind == "refresh":
                    emit("snapshot", data=snapshot(session))
                elif kind == "action":
                    invoke(session, command["action"])
                    text = secrets.clean(transcript.take())
                    if text:
                        emit("output", text=text)
                elif kind == "ip":
                    import requests
                    response = requests.get("https://api.ipify.org", params={"format": "json"})
                    response.raise_for_status()
                    import ipaddress
                    address = str(ipaddress.ip_address(response.json()["ip"]))
                    emit("ip", address=address)
                elif kind == "notification":
                    from desktop.notifications import notification_data
                    for value in command["values"].values():
                        secrets.add(value)
                    data = notification_data(command["channel"], command["values"])
                    session.setSessionData(data, shared=True)
                    emit("configured", channel=command["channel"])
                else:
                    raise ValueError("Commande inconnue")
                if transcript.reported_error:
                    emit("error", code="ErreurSignaléeParLeMoteur")
                else:
                    emit("complete", operation=kind)
            except Exception as exc:
                transcript.take()
                emit("error", code=type(exc).__name__)
    except Cancelled:
        emit("state", state="Annulé")
    except (Exception, SystemExit) as exc:
        emit("error", code=type(exc).__name__)
    finally:
        if session is not None:
            try:
                session.logout()
            except (Exception, SystemExit):
                pass
        if policy:
            policy.close()
        connection.close()
