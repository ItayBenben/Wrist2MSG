"""Messaging service integrations for multiple communication channels."""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError


logger = logging.getLogger(__name__)


class MessagingError(RuntimeError):
    """Raised when a message cannot be delivered via a requested channel."""


@dataclass
class MessagingResult:
    channel: str
    target: Optional[str]
    provider_status: str
    details: Optional[Dict[str, Any]] = None


def send_message(channel: str, contact: Optional[str], message: str) -> MessagingResult:
    """Dispatch a message to the requested communication channel."""

    if not channel:
        raise MessagingError("Channel value is required.")

    normalized = channel.lower().strip()

    if normalized == "whatsapp":
        return _send_via_whatsapp(contact, message)
    if normalized == "telegram":
        return _send_via_telegram(contact, message)
    if normalized == "discord":
        return _send_via_discord(contact, message)

    raise MessagingError(f"Unsupported channel '{channel}'.")


def _send_via_whatsapp(contact: Optional[str], message: str) -> MessagingResult:
    logger.info("Sending WhatsApp message to %s: %s", contact, message)
    # Placeholder for real WhatsApp integration.
    return MessagingResult(channel="whatsapp", target=contact, provider_status="queued")


def _send_via_telegram(contact: Optional[str], message: str) -> MessagingResult:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    default_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    chat_id = contact or default_chat_id

    if not token:
        raise MessagingError("Telegram bot token is not configured.")
    if not chat_id:
        raise MessagingError("Telegram chat ID not provided.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    logger.debug("Posting to Telegram API %s with chat_id=%s", url, chat_id)
    status_code, response_body = _post_json(url, payload)

    logger.info("Telegram message sent to chat_id=%s with status=%s", chat_id, status_code)

    return MessagingResult(
        channel="telegram",
        target=str(chat_id),
        provider_status=str(status_code),
        details={"response": response_body},
    )


def _send_via_discord(contact: Optional[str], message: str) -> MessagingResult:
    default_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    webhook_url = None
    mention_target: Optional[str] = None

    if contact and contact.startswith("http"):
        webhook_url = contact
    else:
        webhook_url = default_webhook_url
        mention_target = contact

    if not webhook_url:
        raise MessagingError("Discord webhook URL is not configured.")

    content = message if mention_target is None else f"{mention_target}: {message}"
    payload = {"content": content}

    logger.debug("Posting to Discord webhook %s", webhook_url)
    status_code, response_body = _post_json(webhook_url, payload)

    logger.info("Discord message sent via webhook with status=%s", status_code)

    return MessagingResult(
        channel="discord",
        target=webhook_url,
        provider_status=str(status_code),
        details={"response": response_body[:2000]},
    )


def _post_json(url: str, payload: Dict[str, Any]) -> Tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    try:
        with urllib_request.urlopen(req, timeout=10) as resp:
            response_body = resp.read().decode("utf-8")
            return resp.getcode(), response_body
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        logger.error("HTTP error posting to %s: %s %s", url, exc.code, body)
        raise MessagingError(f"HTTP error {exc.code} when posting to {url}: {body}") from exc
    except URLError as exc:
        logger.error("Network error posting to %s: %s", url, exc)
        raise MessagingError(f"Network error when posting to {url}: {exc}") from exc

