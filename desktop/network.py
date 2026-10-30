"""Politique requests commune, installée avant tout import réseau du moteur.

En mode proxy, chaque requête impose le proxy choisi, sans repli. Les sockets
du processus sont restreintes à l'hôte du proxy. Ce n'est pas un pare-feu OS.
"""
import ipaddress
import os
import socket
from urllib.parse import urlsplit
import requests


def validate_proxy(value):
    if not value:
        return
    try:
        url = urlsplit(value)
        if url.scheme not in ("http", "https", "socks5h") or not url.hostname or not url.port:
            raise ValueError()
        if url.username is not None or url.password is not None:
            raise ValueError("Les identifiants de proxy dans l'URL ne sont pas pris en charge.")
        if url.path not in ("", "/") or url.query or url.fragment:
            raise ValueError()
    except ValueError as exc:
        raise ValueError("Proxy attendu : http://hôte:port, https://hôte:port ou socks5h://hôte:port, sans identifiants.") from exc


class NetworkPolicy:
    def __init__(self, proxy=""):
        validate_proxy(proxy)
        self.proxy = proxy
        self.original = None
        self.original_send = None
        self.sockets = {}

    def install(self):
        if self.original:
            raise RuntimeError("Politique déjà installée")
        self.original = requests.sessions.Session.request
        self.original_send = requests.sessions.Session.send
        original = self.original
        original_send = self.original_send
        proxy = self.proxy

        def send(session, request, **kwargs):
            # Redirects and prepared requests pass through send, too.
            if urlsplit(request.url).scheme != "https":
                raise requests.exceptions.InvalidURL("Redirection ou requête non HTTPS bloquée.")
            if proxy:
                kwargs["proxies"] = {"http": proxy, "https": proxy, "all": proxy}
            kwargs["verify"] = kwargs.get("verify") if kwargs.get("verify") not in (None, False) else True
            timeout = kwargs.get("timeout")
            if not isinstance(timeout, (int, float, tuple)):
                timeout = (10, 60)
            elif isinstance(timeout, tuple):
                timeout = tuple(min(float(t or 60), 60) for t in timeout)
            else:
                timeout = min(float(timeout), 60)
            kwargs["timeout"] = timeout
            return original_send(session, request, **kwargs)

        def request(session, method, url, **kwargs):
            if urlsplit(url).scheme != "https":
                raise requests.exceptions.InvalidURL("Seules les destinations HTTPS sont autorisées.")
            # Preserve platform proxy/CA bindings in direct mode. The selected
            # profile proxy takes precedence over every engine/per-request proxy.
            if proxy:
                session.trust_env = False
                kwargs["proxies"] = {"http": proxy, "https": proxy, "all": proxy}
            kwargs["verify"] = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("CURL_CA_BUNDLE") or True
            timeout = kwargs.get("timeout")
            if not isinstance(timeout, (int, float, tuple)):
                timeout = (10, 60)
            if isinstance(timeout, tuple):
                timeout = tuple(min(float(t or 60), 60) for t in timeout)
            else:
                timeout = min(float(timeout), 60)
            kwargs["timeout"] = timeout
            return original(session, method, url, **kwargs)

        requests.sessions.Session.request = request
        requests.sessions.Session.send = send
        if proxy:
            try:
                self._restrict_sockets()
            except Exception:
                self.close()
                raise
        return self

    def _restrict_sockets(self):
        parsed = urlsplit(self.proxy)
        allowed = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port, type=socket.SOCK_STREAM)}
        port = parsed.port

        def check(address):
            if not isinstance(address, tuple) or len(address) < 2:
                raise OSError("Communication hors proxy bloquée")
            host = address[0]
            try:
                host = str(ipaddress.ip_address(host))
            except ValueError:
                if host != parsed.hostname:
                    raise OSError("Communication hors proxy bloquée")
            if address[1] != port or (host not in allowed and host != parsed.hostname):
                raise OSError("Communication hors proxy bloquée")

        for name in ("connect", "connect_ex", "sendto"):
            original = getattr(socket.socket, name)
            self.sockets[name] = original

            def guarded(sock, *args, _name=name, _original=original, **kwargs):
                address = args[-1] if _name == "sendto" else args[0]
                check(address)
                return _original(sock, *args, **kwargs)

            setattr(socket.socket, name, guarded)

    def close(self):
        if self.original:
            requests.sessions.Session.request = self.original
            requests.sessions.Session.send = self.original_send
            self.original = None
        for name, original in self.sockets.items():
            setattr(socket.socket, name, original)
        self.sockets.clear()

    def __enter__(self):
        return self.install()

    def __exit__(self, *args):
        self.close()
