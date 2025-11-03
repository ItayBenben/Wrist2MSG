import datetime
import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Dict

from flask import Flask, jsonify, request


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure logging only when running as the main module."""
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@dataclass(frozen=True)
class MessageRequest:
    contact: str
    message: str

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "MessageRequest":
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")

        contact = payload.get("contact")
        message = payload.get("message")

        if not isinstance(contact, str) or not contact.strip():
            raise ValueError("'contact' must be a non-empty string")

        if not isinstance(message, str) or not message.strip():
            raise ValueError("'message' must be a non-empty string")

        return cls(contact=contact.strip(), message=message.strip())


class MessageService:
    def __init__(self, transport: Callable[[str, str], None] | None = None) -> None:
        self._transport = transport or self._default_transport

    def send(self, request_dto: MessageRequest) -> None:
        self._transport(request_dto.contact, request_dto.message)

    @staticmethod
    def _default_transport(contact: str, message: str) -> None:
        logger.info("Dispatching WhatsApp message to %s", contact)
        logger.debug("Message content: %s", message)


app = Flask(__name__)
message_service = MessageService()


@app.route("/send", methods=["POST"])
def send_message() -> tuple[Any, int] | Any:
    payload = request.get_json(silent=True)

    try:
        message_request = MessageRequest.from_payload(payload or {})
    except ValueError as exc:
        logger.warning("Invalid message payload: %s", exc)
        return (
            jsonify({"status": "error", "error": str(exc)}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        message_service.send(message_request)
    except Exception:  # pragma: no cover - placeholder for real transport errors
        logger.exception("Failed to dispatch message")
        return (
            jsonify({"status": "error", "error": "Failed to send message"}),
            HTTPStatus.BAD_GATEWAY,
        )

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return jsonify({
        "status": "sent",
        "recipient": message_request.contact,
        "timestamp": timestamp,
    })


if __name__ == "__main__":
    configure_logging()
    app.run(host="0.0.0.0", port=8080)
