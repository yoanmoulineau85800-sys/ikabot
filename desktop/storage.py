"""Métadonnées sans secrets et historique SQLite transactionnel."""
import json
import sqlite3
import uuid
from pathlib import Path


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "desktop.sqlite3")
        self.db.executescript("""
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS profiles(id TEXT PRIMARY KEY, name TEXT NOT NULL,
            email TEXT NOT NULL, server TEXT NOT NULL, proxy TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, at TEXT DEFAULT
            (strftime('%Y-%m-%dT%H:%M:%SZ','now')), profile TEXT, message TEXT);
          CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        """)
        self.db.commit()

    def profiles(self):
        return [dict(zip(("id", "name", "email", "server", "proxy"), row))
                for row in self.db.execute("SELECT * FROM profiles ORDER BY name")]

    def save_profile(self, name, email, server, proxy="", profile_id=None):
        from desktop.network import validate_proxy
        if not name.strip() or not email.strip():
            raise ValueError("Le nom et l'adresse e-mail sont obligatoires.")
        validate_proxy(proxy)
        profile_id = profile_id or uuid.uuid4().hex
        self.db.execute("INSERT OR REPLACE INTO profiles VALUES (?,?,?,?,?)",
                        (profile_id, name.strip(), email.strip(), server.strip(), proxy.strip()))
        self.db.commit()
        return profile_id

    def delete_profile(self, profile_id):
        self.db.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
        self.db.commit()

    def event(self, profile, message):
        # Only caller-generated status messages belong here, never engine output.
        self.db.execute("INSERT INTO events(profile,message) VALUES (?,?)", (profile, message))
        self.db.commit()

    def events(self):
        return list(self.db.execute("SELECT at,profile,message FROM events ORDER BY id DESC LIMIT 500"))

    def setting(self, key, default=None):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, json.dumps(value)))
        self.db.commit()
