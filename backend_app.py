from flask import Flask, request, jsonify
import datetime

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
