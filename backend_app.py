from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    contact = data.get('contact')
    message = data.get('message')
    print(f"Sending WhatsApp message to {contact}: {message}")
    return jsonify({'status': 'sent', 'timestamp': datetime.datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
