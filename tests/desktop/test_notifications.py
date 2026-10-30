import pytest
from desktop.notifications import notification_data


def test_notification_data_matches_engine_schema_without_network():
    token = "12345:" + "a" * 25
    assert notification_data("telegram", {"token": token, "chat": "-123"}) == {
        "telegram": {"botToken": token, "chatId": "-123"}}
    url = "https://discord.com/api/webhooks/123/abcdef"
    assert notification_data("discord", {"webhook": url}) == {"discord": {"webhookUrl": url}}


@pytest.mark.parametrize("channel,values", [
    ("telegram", {"token": "invalid", "chat": "1"}),
    ("telegram", {"token": "123:" + "x" * 25, "chat": "not a chat"}),
    ("discord", {"webhook": "http://discord.com/api/webhooks/1/token"}),
    ("discord", {"webhook": "https://evil.example/api/webhooks/1/token"}),
    ("discord", {"webhook": "https://discord.com/api/webhooks/1/token?secret=1"}),
])
def test_invalid_notification_parameters_are_rejected(channel, values):
    with pytest.raises(ValueError):
        notification_data(channel, values)
