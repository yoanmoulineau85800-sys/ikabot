"""Configuration native compatible avec le stockage du moteur, sans envoi implicite."""
import re
from urllib.parse import urlsplit


def notification_data(channel, values):
    if channel == "telegram":
        token = values.get("token", "").strip()
        chat = values.get("chat", "").strip()
        if not re.fullmatch(r"\d+:[A-Za-z0-9_-]{20,}", token) or not re.fullmatch(r"-?\d+", chat):
            raise ValueError("Indiquez un jeton Telegram valide et un identifiant numérique de conversation.")
        return {"telegram": {"botToken": token, "chatId": chat}}
    if channel == "discord":
        webhook = values.get("webhook", "").strip()
        url = urlsplit(webhook)
        if url.scheme != "https" or url.hostname not in ("discord.com", "discordapp.com") or not re.fullmatch(r"/api/webhooks/\d+/[A-Za-z0-9_-]+", url.path) or url.username or url.query or url.fragment or url.port not in (None, 443):
            raise ValueError("Indiquez une URL HTTPS officielle de webhook Discord.")
        return {"discord": {"webhookUrl": webhook}}
    raise ValueError("Canal de notification inconnu")
