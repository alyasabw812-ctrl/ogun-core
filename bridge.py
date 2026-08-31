import subprocess
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

def run_termux_cmd(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout.strip()}
        elif result.returncode == 0:
            return {"status": "success"}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "exception", "error": str(e)}

@app.route('/api/status', methods=['GET'])
def get_status():
    battery = run_termux_cmd("termux-battery-status")
    wifi = run_termux_cmd("termux-wifi-connectioninfo")
    return jsonify({
        "status": "online",
        "system": "Ogun Local Bridge v1.0",
        "battery": battery,
        "wifi": wifi
    })

@app.route('/api/speak', methods=['POST'])
def speak():
    data = request.get_json() or {}
    text = data.get('text', 'أنا في الخدمة يا سيدي')
    run_termux_cmd(f'termux-tts-speak "{text}"')
    return jsonify({"status": "speaking", "text": text})

@app.route('/api/torch', methods=['POST'])
def toggle_torch():
    data = request.get_json() or {}
    state = data.get('state', 'off')
    run_termux_cmd(f'termux-torch {state}')
    return jsonify({"status": "torch", "state": state})

@app.route('/api/notify', methods=['POST'])
def send_notification():
    data = request.get_json() or {}
    title = data.get('title', 'Ogun System')
    content = data.get('content', '')
    run_termux_cmd(f'termux-notification -t "{title}" -c "{content}"')
    return jsonify({"status": "notified"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
