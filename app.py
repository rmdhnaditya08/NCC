from flask import Flask, request, jsonify
from datetime import datetime, timezone
import json
import os
import time

app = Flask(__name__)

START_TIME = time.time()

LOG_FILE = "/app/logs/webhooks.json"
os.makedirs("/app/logs", exist_ok=True)

def read_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def write_log(entry):
    logs = read_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_uptime():
    seconds = int(time.time() - START_TIME)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{days}d {hours}h {minutes}m {secs}s"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "200 OK",
        "message": "Service is running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": get_uptime()
    }), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json(silent=True) or request.data.decode()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "headers": dict(request.headers),
        "payload": payload
    }
    write_log(entry)
    print(f"[WEBHOOK] {entry['timestamp']} - received payload")
    return jsonify({"status": "received"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(read_logs()), 200

@app.route("/logs/clear", methods=["DELETE"])
def clear_logs():
    with open(LOG_FILE, "w") as f:
        json.dump([], f)
    return jsonify({"status": "logs cleared"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
