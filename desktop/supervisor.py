"""Supervision Qt non bloquante : un processus et une opération par profil."""
import multiprocessing
import time
import psutil
from PySide6.QtCore import QObject, QTimer, Signal
from desktop.engine import run_worker


class Supervisor(QObject):
    message = Signal(str, dict)

    def __init__(self, root):
        super().__init__()
        self.root = str(root)
        self.workers = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(80)

    def start(self, profile):
        key = profile["id"]
        if key in self.workers:
            raise ValueError("Ce profil possède déjà une session active.")
        for worker in self.workers.values():
            other = worker["profile"]
            if profile["email"].casefold() == other["email"].casefold() and (
                not profile.get("server") or not other.get("server") or profile["server"].casefold() == other["server"].casefold()):
                raise ValueError("Ce compte possède déjà une session sur ce serveur (ou un serveur non précisé).")
        parent, child = multiprocessing.get_context("spawn").Pipe()
        process = multiprocessing.get_context("spawn").Process(
            target=run_worker, args=(child, profile, self.root), daemon=False)
        process.start()
        child.close()
        self.workers[key] = {"process": process, "pipe": parent, "idle": False, "prompt": False, "profile": dict(profile)}

    def send(self, key, command, **fields):
        worker = self.workers.get(key)
        if not worker:
            raise ValueError("Connectez d'abord le profil.")
        if command == "answer":
            if not worker["prompt"]:
                raise ValueError("Aucune réponse attendue.")
            worker["prompt"] = False
        elif command not in ("cancel", "quit"):
            if not worker["idle"]:
                raise ValueError("Une opération est déjà en cours sur ce profil.")
            worker["idle"] = False
        worker["pipe"].send({"command": command, **fields})

    def poll(self):
        for key, worker in list(self.workers.items()):
            try:
                # Bound each tick so a noisy worker cannot freeze the GUI.
                for _ in range(40):
                    if not worker["pipe"].poll():
                        break
                    message = worker["pipe"].recv()
                    if message["type"] == "idle":
                        worker["idle"] = True
                    if message["type"] == "prompt":
                        worker["prompt"] = True
                    self.message.emit(key, message)
            except (EOFError, OSError):
                pass
            if not worker["process"].is_alive():
                self._remove(key)

    def _remove(self, key):
        worker = self.workers.pop(key, None)
        if worker:
            worker["process"].join(timeout=0)
            worker["pipe"].close()
            self.message.emit(key, {"type": "stopped"})

    def stop(self, key):
        worker = self.workers.get(key)
        if not worker:
            return
        # Never signal arbitrary saved PIDs: only the owned process tree.
        try:
            parent = psutil.Process(worker["process"].pid)
            children = parent.children(recursive=True)
        except psutil.NoSuchProcess:
            children = []
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        if worker["process"].is_alive():
            worker["process"].terminate()
        _, alive = psutil.wait_procs(children, timeout=0.5)
        for child in alive:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        worker["process"].join(timeout=0.5)
        if worker["process"].is_alive():
            worker["process"].kill()
            worker["process"].join(timeout=0.5)
        if worker["process"].is_alive():
            raise RuntimeError("Impossible de confirmer l'arrêt du processus du profil.")
        self._remove(key)

    def shutdown(self):
        self.timer.stop()
        for key, worker in list(self.workers.items()):
            if worker["idle"]:
                try:
                    self.send(key, "quit")
                except (OSError, ValueError):
                    pass
        deadline = time.monotonic() + 1
        for worker in list(self.workers.values()):
            worker["process"].join(timeout=max(0, deadline - time.monotonic()))
        for key in list(self.workers):
            self.stop(key)
