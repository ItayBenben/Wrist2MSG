import datetime
import logging
from abc import ABC, abstractmethod
from typing import Dict

from flask import Flask, jsonify, request


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessagingInterface(ABC):
    """Base class for supported messaging interfaces."""

    name: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    @abstractmethod
    def send(self, contact: str, message: str) -> None:
        """Send the message to the target contact."""


class WhatsAppInterface(MessagingInterface):
    name = "whatsapp"

    def send(self, contact: str, message: str) -> None:  # pragma: no cover - placeholder integration
        logger.info("Sending WhatsApp message to %s: %s", contact, message)


class TelegramInterface(MessagingInterface):
    name = "telegram"

    def send(self, contact: str, message: str) -> None:  # pragma: no cover - placeholder integration
        logger.info("Sending Telegram message to %s: %s", contact, message)


class DiscordInterface(MessagingInterface):
    name = "discord"

    def send(self, contact: str, message: str) -> None:  # pragma: no cover - placeholder integration
        logger.info("Sending Discord message to %s: %s", contact, message)


def _build_interface_registry() -> Dict[str, MessagingInterface]:
    interfaces = [
        WhatsAppInterface(),
        TelegramInterface(),
        DiscordInterface(),
    ]
    return {interface.name: interface for interface in interfaces}


INTERFACES = _build_interface_registry()

app = Flask(__name__)


@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    contact = data.get("contact")
    message = data.get("message")
    interface_name = (data.get("interface") or WhatsAppInterface.name).lower()

    if not contact or not message:
        return (
            jsonify(
                {
                    "error": "contact and message are required",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            ),
            400,
        )

    interface = INTERFACES.get(interface_name)
    if interface is None:
        return (
            jsonify(
                {
                    "error": f"unsupported interface '{interface_name}'",
                    "supported_interfaces": sorted(INTERFACES),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            ),
            400,
        )

    interface.send(contact, message)

    return jsonify(
        {
            "status": "sent",
            "interface": interface.name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
    )


@app.route("/interfaces", methods=["GET"])
def list_interfaces():
    return jsonify(
        {
            "interfaces": sorted(INTERFACES),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
