"""Véritables sockets, serveur HTTPS et proxy CONNECT isolés du client testé."""
import datetime
import multiprocessing
import select
import socket
import ssl
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import StreamRequestHandler, ThreadingTCPServer
import pytest
import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from desktop.network import NetworkPolicy, validate_proxy


def servers(pipe, root):
    root = Path(root)
    class Origin(BaseHTTPRequestHandler):
        def do_GET(self):
            with (root / "hits").open("a") as f:
                f.write("origin\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        def log_message(self, *args):
            pass
    origin = ThreadingHTTPServer(("127.0.0.1", 0), Origin)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(root / "cert.pem", root / "key.pem")
    origin.socket = context.wrap_socket(origin.socket, server_side=True)
    threading.Thread(target=origin.serve_forever, daemon=True).start()

    class Proxy(StreamRequestHandler):
        def handle(self):
            request = self.rfile.readline().decode()
            while self.rfile.readline() not in (b"\r\n", b"\n", b""):
                pass
            if (root / "down").exists():
                return
            if (root / "error").exists():
                self.wfile.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
                return
            target = request.split()[1]
            host, port = target.rsplit(":", 1)
            with socket.create_connection((host, int(port)), timeout=3) as remote:
                self.wfile.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
                self.wfile.flush()
                while True:
                    ready, _, _ = select.select([self.connection, remote], [], [], 3)
                    if not ready:
                        break
                    for source in ready:
                        data = source.recv(65536)
                        if not data:
                            return
                        (remote if source is self.connection else self.connection).sendall(data)
    proxy = ThreadingTCPServer(("127.0.0.1", 0), Proxy)
    proxy.daemon_threads = True
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    pipe.send((origin.server_port, proxy.server_address[1]))
    pipe.recv()
    proxy.shutdown()
    origin.shutdown()


@pytest.fixture
def https_proxy(tmp_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.timezone.utc)
    import ipaddress
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=1))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(key, hashes.SHA256()))
    (tmp_path / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (tmp_path / "key.pem").write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    parent, child = multiprocessing.get_context("spawn").Pipe()
    process = multiprocessing.get_context("spawn").Process(target=servers, args=(child, str(tmp_path)))
    process.start()
    child.close()
    assert parent.poll(15), "Le serveur HTTPS local n'a pas démarré"
    ports = parent.recv()
    try:
        yield tmp_path, ports
    finally:
        parent.send("stop")
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join(3)
        parent.close()


def test_real_proxy_outage_and_error_never_fall_back_to_origin(https_proxy, monkeypatch):
    root, (origin_port, proxy_port) = https_proxy
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(root / "cert.pem"))
    url = f"https://127.0.0.1:{origin_port}/"
    proxy = f"http://127.0.0.1:{proxy_port}"
    with NetworkPolicy(proxy):
        assert requests.get(url, timeout=3, proxies={}).json() == {"ok": True}
        assert (root / "hits").read_text().count("origin") == 1
        (root / "down").touch()
        with pytest.raises(requests.RequestException):
            requests.get(url, timeout=3, proxies={})
        (root / "down").unlink()
        (root / "error").touch()
        with pytest.raises(requests.RequestException):
            requests.get(url, timeout=3)
        assert (root / "hits").read_text().count("origin") == 1
        with pytest.raises(OSError, match="hors proxy"):
            socket.create_connection(("127.0.0.1", origin_port), timeout=1)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
            with pytest.raises(OSError, match="hors proxy"):
                udp.sendto(b"DNS leak probe", ("127.0.0.1", 53))


def test_tls_verification_cannot_be_disabled(https_proxy, monkeypatch):
    root, (origin_port, proxy_port) = https_proxy
    monkeypatch.delenv("REQUESTS_CA_BUNDLE", raising=False)
    monkeypatch.delenv("CURL_CA_BUNDLE", raising=False)
    with NetworkPolicy(f"http://127.0.0.1:{proxy_port}"):
        with pytest.raises(requests.exceptions.SSLError):
            requests.get(f"https://127.0.0.1:{origin_port}/", verify=False, timeout=3)
    assert not (root / "hits").exists()


def test_plain_http_prepared_request_is_blocked():
    with NetworkPolicy():
        session = requests.Session()
        prepared = session.prepare_request(requests.Request("GET", "http://example.org"))
        with pytest.raises(requests.exceptions.InvalidURL):
            session.send(prepared, verify=False)


@pytest.mark.parametrize("proxy", ["socks5://host:1", "http://u:p@host:8080", "http://host", "http://host:2/path"])
def test_invalid_or_locally_resolving_proxy_is_rejected(proxy):
    with pytest.raises(ValueError):
        validate_proxy(proxy)
