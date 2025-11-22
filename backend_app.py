import datetime
import hmac
import os
from typing import Dict, Optional

from flask import Flask, jsonify, request

from messaging_service import (
    MessagingConfigurationError,
    MessagingError,
    MessagingHTTPError,
    MessagingNetworkError,
    MessagingService,
    UnsupportedPlatformError,
)

app = Flask(__name__)
messaging_service = MessagingService()


def _load_device_tokens() -> Dict[str, str]:
    """Parse WATCH_DEVICE_TOKENS env var into {device_id: token} map."""
    raw = os.getenv("WATCH_DEVICE_TOKENS", "")
    tokens: Dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        device_id, token = entry.split(":", 1)
        tokens[device_id.strip()] = token.strip()
    return tokens


DEVICE_TOKENS = _load_device_tokens()


def _is_authorized_device(device_id: Optional[str], auth_header: Optional[str]) -> bool:
    if not device_id or not auth_header or not auth_header.startswith("Bearer "):
        return False
    provided_token = auth_header.split(" ", 1)[1].strip()
    expected_token = DEVICE_TOKENS.get(device_id)
    if not expected_token:
        return False
    return hmac.compare_digest(provided_token, expected_token)

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json(silent=True) or {}
    platform = data.get('platform', 'whatsapp')
    contact = data.get('contact')
    message = data.get('message', '')
    metadata = data.get('metadata') or {}

    if not message:
        return jsonify({'error': 'message is required'}), 400

    if metadata and not isinstance(metadata, dict):
        return jsonify({'error': 'metadata must be an object/dict'}), 400

    try:
        delivery_info = messaging_service.send(
            platform=platform,
            contact=contact,
            message=message,
            metadata=metadata,
        )
    except UnsupportedPlatformError as exc:
        return jsonify({'error': str(exc)}), 400
    except MessagingConfigurationError as exc:
        return jsonify({'error': str(exc)}), 422
    except MessagingNetworkError as exc:
        return jsonify({'error': str(exc)}), 503
    except MessagingHTTPError as exc:
        return jsonify({'error': str(exc), 'status_code': exc.status_code}), 502
    except MessagingError as exc:
        return jsonify({'error': str(exc)}), 500

    timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    response_payload = {
        'status': 'sent',
        'platform': delivery_info.get('platform', platform),
        'contact': delivery_info.get('contact', contact),
        'details': delivery_info,
        'timestamp': timestamp,
    }
    return jsonify(response_payload)
 
@app.route('/watch/send', methods=['POST'])
def relay_send_message():
    device_id = request.headers.get('X-Device-ID')
    auth_header = request.headers.get('Authorization')

    if not _is_authorized_device(device_id, auth_header):
        return jsonify({'error': 'unauthorized device'}), 401

    payload = request.get_json(silent=True) or {}
    message = payload.get('message')
    if not message:
        return jsonify({'error': 'message is required'}), 400

    platform = (payload.get('platform') or 'whatsapp').lower()
    contact = payload.get('contact') or payload.get('contact_id')
    metadata = payload.get('metadata') or {}

    relay_meta = {
        'relay_source': 'garmin_direct',
        'device_id': device_id,
        'device_firmware': payload.get('firmware'),
        'relay_nonce': request.headers.get('X-Device-Nonce'),
        'message_id': payload.get('message_id'),
    }

    if isinstance(metadata, dict):
        metadata.update({k: v for k, v in relay_meta.items() if v})
    else:
        metadata = {k: v for k, v in relay_meta.items() if v}

    try:
        delivery_info = messaging_service.send(
            platform=platform,
            contact=contact,
            message=message,
            metadata=metadata,
        )
    except UnsupportedPlatformError as exc:
        return jsonify({'error': str(exc)}), 400
    except MessagingConfigurationError as exc:
        return jsonify({'error': str(exc)}), 422
    except MessagingNetworkError as exc:
        return jsonify({'error': str(exc)}), 503
    except MessagingHTTPError as exc:
        return jsonify({'error': str(exc), 'status_code': exc.status_code}), 502
    except MessagingError as exc:
        return jsonify({'error': str(exc)}), 500

    timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    response_payload = {
        'status': 'queued',
        'platform': delivery_info.get('platform', platform),
        'contact': delivery_info.get('contact', contact),
        'details': delivery_info,
        'timestamp': timestamp,
    }
    return jsonify(response_payload), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
