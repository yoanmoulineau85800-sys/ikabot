from desktop.supervisor import Supervisor


def test_real_worker_reaches_graphical_password_prompt_and_cancels(qtbot, tmp_path):
    supervisor = Supervisor(tmp_path)
    messages = []
    supervisor.message.connect(lambda key, message: messages.append((key, message)))
    profile = {"id": "test-isole", "name": "Test", "email": "desktop-test@example.invalid", "server": "", "proxy": ""}
    try:
        supervisor.start(profile)
        qtbot.waitUntil(lambda: any(m["type"] == "prompt" for _, m in messages), timeout=15000)
        prompt = next(m for _, m in messages if m["type"] == "prompt")
        assert prompt["secret"] is True
        assert "Password" in prompt["message"]
        assert "test-isole" in supervisor.workers
        supervisor.send("test-isole", "cancel")
        qtbot.waitUntil(lambda: not supervisor.workers, timeout=5000)
        assert any(m["type"] == "stopped" for _, m in messages)
        assert not any(m["type"] == "snapshot" for _, m in messages)
    finally:
        supervisor.shutdown()


def test_duplicate_account_is_rejected_before_process_creation(qtbot, tmp_path):
    import pytest
    supervisor = Supervisor(tmp_path)
    profile = {"id": "a", "name": "Test", "email": "duplicate@example.invalid", "server": "", "proxy": ""}
    try:
        supervisor.start(profile)
        with pytest.raises(ValueError, match="déjà"):
            supervisor.start({**profile, "id": "b"})
    finally:
        supervisor.shutdown()
