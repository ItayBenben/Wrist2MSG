from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    contact = data.get('contact')
    message = data.get('message')
    platform = (data.get('platform') or 'whatsapp').lower()

    if not contact or not message:
        return jsonify({'error': 'contact and message are required'}), 400

    if platform not in {'whatsapp', 'telegram', 'discord'}:
        return jsonify({'error': 'unsupported platform'}), 400

    print(f"Routing message via {platform} to {contact}: {message}")
    # TODO: integrate provider adapters here
    return jsonify({
        'status': 'queued',
        'platform': platform,
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
