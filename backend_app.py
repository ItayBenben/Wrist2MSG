import datetime
import logging

from flask import Flask, request, jsonify

from messaging_services import MessagingError, send_message

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/send', methods=['POST'])
def send_message_route():
    data = request.get_json(silent=True) or {}
    contact = data.get('contact')
    message = data.get('message')
    channel = (data.get('channel') or 'whatsapp').strip().lower()

    if not message:
        return jsonify({'status': 'error', 'error': 'Message content is required.'}), 400

    try:
        result = send_message(channel, contact, message)
    except MessagingError as exc:
        logger.warning('Messaging error for channel=%s: %s', channel, exc)
        return jsonify({'status': 'error', 'error': str(exc), 'channel': channel}), 400
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception('Unexpected error while sending message via %s', channel)
        return jsonify({'status': 'error', 'error': 'Internal server error.'}), 500

    response_payload = {
        'status': 'sent',
        'channel': result.channel,
        'target': result.target,
        'provider_status': result.provider_status,
        'timestamp': datetime.datetime.utcnow().isoformat(),
    }

    if result.details:
        response_payload['details'] = result.details

    return jsonify(response_payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
