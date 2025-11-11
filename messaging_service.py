import json
import os
from typing import Any, Dict, Optional, Tuple
import urllib.error
import urllib.request


class MessagingError(Exception):
    """Base exception for messaging errors."""


class UnsupportedPlatformError(MessagingError):
    """Raised when an unsupported messaging platform is requested."""


class MessagingConfigurationError(MessagingError):
    """Raised when required configuration is missing."""


class MessagingNetworkError(MessagingError):
    """Raised when a network error occurs during message delivery."""


class MessagingHTTPError(MessagingError):
    """Raised when the remote service returns an HTTP error."""

    def __init__(self, url: str, status_code: int, response_body: Optional[str] = None) -> None:
        super().__init__(f"HTTP {status_code} from {url}: {response_body or 'No body'}")
        self.url = url
        self.status_code = status_code
        self.response_body = response_body


class MessagingService:
    """Dispatches outbound messages to supported platforms."""

    def __init__(
        self,
        *,
        telegram_bot_token: Optional[str] = None,
        discord_default_webhook: Optional[str] = None,
        request_timeout_seconds: Optional[float] = None,
    ) -> None:
        self.telegram_bot_token = telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.discord_default_webhook = discord_default_webhook or os.getenv("DISCORD_WEBHOOK_URL")
        timeout_value = request_timeout_seconds or os.getenv("MESSAGE_REQUEST_TIMEOUT_SECONDS", "10")
        self.request_timeout_seconds = float(timeout_value)

    def send(
        self,
        *,
        platform: str,
        contact: Optional[str],
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        platform_key = (platform or "whatsapp").strip().lower()
        metadata = metadata or {}

        if platform_key == "whatsapp":
            return self._send_whatsapp(contact=contact, message=message, metadata=metadata)

        if platform_key == "telegram":
            return self._send_telegram(chat_id=contact, message=message, metadata=metadata)

        if platform_key == "discord":
            return self._send_discord(webhook_url=contact, message=message, metadata=metadata)

        raise UnsupportedPlatformError(f"Unsupported messaging platform: {platform}")

    def _send_whatsapp(
        self,
        *,
        contact: Optional[str],
        message: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Placeholder for WhatsApp integration. For now, we keep the existing logging behaviour.
        print(f"Sending WhatsApp message to {contact or 'default'}: {message}")
        return {
            "platform": "whatsapp",
            "contact": contact,
            "metadata_echo": metadata or None,
            "delivery_hint": "Message logged for WhatsApp delivery.",
        }

    def _send_telegram(
        self,
        *,
        chat_id: Optional[str],
        message: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.telegram_bot_token:
            raise MessagingConfigurationError("TELEGRAM_BOT_TOKEN is not configured.")

        if not chat_id:
            raise MessagingConfigurationError("Telegram chat_id (contact) is required.")

        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": message,
        }

        parse_mode = metadata.get("parse_mode")
        disable_notification = metadata.get("disable_notification")
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if disable_notification is not None:
            payload["disable_notification"] = bool(disable_notification)

        status_code, response_body = self._post_json(url, payload)

        if status_code != 200:
            raise MessagingHTTPError(url, status_code, self._stringify_body(response_body))

        if not isinstance(response_body, dict) or not response_body.get("ok"):
            raise MessagingError(f"Unexpected Telegram response: {response_body!r}")

        result: Dict[str, Any] = response_body.get("result", {})
        return {
            "platform": "telegram",
            "chat_id": chat_id,
            "message_id": result.get("message_id"),
            "date": result.get("date"),
        }

    def _send_discord(
        self,
        *,
        webhook_url: Optional[str],
        message: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        target_webhook = webhook_url or self.discord_default_webhook

        if not target_webhook:
            raise MessagingConfigurationError(
                "Discord webhook URL is not provided. Supply it as the contact field or set DISCORD_WEBHOOK_URL."
            )

        payload: Dict[str, Any] = {
            "content": message,
        }

        username = metadata.get("username")
        avatar_url = metadata.get("avatar_url")
        embeds = metadata.get("embeds")

        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if embeds:
            payload["embeds"] = embeds

        status_code, response_body = self._post_json(target_webhook, payload)

        if status_code not in (200, 204):
            raise MessagingHTTPError(target_webhook, status_code, self._stringify_body(response_body))

        discord_message_id = None
        if isinstance(response_body, dict):
            discord_message_id = response_body.get("id")

        return {
            "platform": "discord",
            "webhook_url": target_webhook,
            "message_id": discord_message_id,
            "status_code": status_code,
        }

    def _post_json(self, url: str, payload: Dict[str, Any]) -> Tuple[int, Optional[Any]]:
        encoded_payload = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        request = urllib.request.Request(url, data=encoded_payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=self.request_timeout_seconds) as response:
                status_code = response.getcode()
                raw_body = response.read()
                if not raw_body:
                    return status_code, None

                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return status_code, json.loads(raw_body.decode("utf-8"))
                return status_code, raw_body.decode("utf-8")

        except urllib.error.HTTPError as exc:
            body_bytes = exc.read()
            response_body = body_bytes.decode("utf-8") if body_bytes else None
            raise MessagingHTTPError(url, exc.code, response_body) from exc
        except urllib.error.URLError as exc:
            raise MessagingNetworkError(f"Network error when calling {url}: {exc.reason}") from exc

    @staticmethod
    def _stringify_body(body: Optional[Any]) -> Optional[str]:
        if body is None:
            return None
        if isinstance(body, str):
            return body
        try:
            return json.dumps(body)
        except (TypeError, ValueError):
            return str(body)
