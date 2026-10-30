import os
import pytest
from desktop.storage import Store
from desktop.security import protect, unprotect, save_secret


def test_profiles_and_preferences_survive_restart(tmp_path):
    store = Store(tmp_path)
    key = store.save_profile("Compte", "joueur@example.org", "s1-fr.ikariam.gameforge.com")
    store.set_setting("theme", "clair")
    store.event("Compte", "Connexion demandée")
    store.db.close()
    restored = Store(tmp_path)
    assert restored.profiles()[0]["id"] == key
    assert restored.setting("theme") == "clair"
    assert restored.events()[0][2] == "Connexion demandée"
    restored.save_profile("Nouveau nom", "joueur@example.org", "s1-fr.ikariam.gameforge.com", profile_id=key)
    assert len(restored.profiles()) == 1
    restored.delete_profile(key)
    assert restored.profiles() == []


def test_credentials_never_allowed_in_proxy_metadata(tmp_path):
    store = Store(tmp_path)
    with pytest.raises(ValueError):
        store.save_profile("Compte", "a@b.fr", "", "http://user:password@127.0.0.1:8080")
    assert store.profiles() == []


@pytest.mark.skipif(os.name == "nt", reason="Test du refus de repli hors Windows")
def test_non_windows_secret_storage_fails_closed(tmp_path):
    path = tmp_path / "secret"
    with pytest.raises(RuntimeError):
        save_secret(path, b"secret-value")
    assert not path.exists()


@pytest.mark.skipif(os.name != "nt", reason="DPAPI nécessite un véritable utilisateur Windows")
def test_windows_dpapi_round_trip_and_tampering(tmp_path):
    secret = b"mot-de-passe-et-cookie"
    path = tmp_path / "vault"
    save_secret(path, secret)
    assert secret not in path.read_bytes()
    assert unprotect(path.read_bytes()) == secret
    damaged = bytearray(path.read_bytes())
    damaged[-10] ^= 0xFF
    with pytest.raises(OSError):
        unprotect(bytes(damaged))
