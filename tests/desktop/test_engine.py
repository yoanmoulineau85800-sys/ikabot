from types import SimpleNamespace
import threading
import pytest
from desktop.catalog import ACTIONS
from desktop.engine import invoke, snapshot, SecretFilter
from desktop.engine import snapshot_movements


def test_every_available_action_obeys_real_engine_contract():
    import importlib
    for action in ACTIONS.values():
        function = getattr(importlib.import_module(action.module), action.function)
        if not action.reason:
            assert function._is_configurator, action.function


def test_adapter_runs_original_configuration_then_original_task(monkeypatch):
    from ikabot.function import sendResources
    from ikabot.helpers.decorators import _TASK_REGISTRY
    calls = []
    session = object()
    def configure(s, event, stdin_fd, inputs):
        assert s is session and stdin_fd is None and inputs == []
        calls.append("configuration")
        return {"session": s, "routes": ["route"], "useFreighters": False}
    def task(**kwargs):
        assert kwargs["session"] is session and kwargs["routes"] == ["route"]
        calls.append("task")
    monkeypatch.setattr(sendResources.sendResources, "__wrapped__", configure)
    monkeypatch.setitem(_TASK_REGISTRY, "sendResources", SimpleNamespace(__wrapped__=task))
    invoke(session, "sendResources")
    assert calls == ["configuration", "task"]


def test_unavailable_code_cannot_be_invoked():
    with pytest.raises(ValueError):
        invoke(None, "loadCustomModule")


def test_snapshot_projects_only_city_fields(monkeypatch):
    from ikabot.helpers import pedirInfo, getJson
    monkeypatch.setattr(pedirInfo, "getIdsOfCities", lambda s: (["12"], {}))
    monkeypatch.setattr(getJson, "getCity", lambda html: {
        "name": "Athènes", "availableResources": [1, 2, 3, 4, 5], "x": 5, "y": 8,
        "cookie": "secret", "position": [{"building": "townHall", "level": 12, "isBusy": True}]})
    data = snapshot(SimpleNamespace(get=lambda url: "real parser fixture elsewhere", urlBase="https://s1-fr.ikariam.gameforge.com/index.php?token=secret"))
    assert data["cities"][0]["resources"] == [1, 2, 3, 4, 5]
    assert "cookie" not in repr(data) and "token" not in data["server"]


def test_known_secrets_and_header_values_are_redacted():
    cleaner = SecretFilter()
    cleaner.add("very-secret-password")
    assert "very-secret-password" not in cleaner.clean("very-secret-password")
    assert "cookievalue" not in cleaner.clean("Cookie: cookievalue")
    assert "pass@" not in cleaner.clean("https://user:pass@host/path")


def test_movement_projection_uses_the_engine_response_path(monkeypatch):
    import json
    from ikabot.helpers import varios
    monkeypatch.setattr(varios, "getCurrentCityId", lambda s: "42")
    movement = {"origin": {"name": "Athènes", "cookie": "not transferred"}, "target": {"name": "Rome"},
                "event": {"missionText": "Transport", "isFleetReturning": False},
                "eventTime": 1700000000, "isHostile": True, "token": "not transferred"}
    response = [None, [None, [None, None, {"viewScriptParams": {"militaryAndFleetMovements": [movement]}}]]]
    session = SimpleNamespace(post=lambda url: json.dumps(response))
    data = snapshot_movements(session)
    assert data[0]["origin"] == "Athènes" and data[0]["hostile"]
    assert "cookie" not in repr(data) and "token" not in repr(data)
