# -*- coding: utf-8 -*-
import json
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------- CONFIG ----------
# REPLACE THIS WITH YOUR NEW TOKEN AFTER REVOKING!
BOT_TOKEN = "8652420850:AAGV_YjffZZ9BPH_WROZRNIrZyMxBg3EsnM"
ALLOWED_USER_ID = 5425390323

CONFIG_FILE = "config.json"
COUNT_FILE = "count.txt"
STATUS_FILE = "status.txt"
CONV_STATE_FILE = "conv_state.txt"

# ---------- Helper functions ----------
def send_message(chat_id, text, parse_mode=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

def load_config():
    default = {"vr_title1": "", "vr_title2": "", "vr_announcement": "", "enabled": False}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return default

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def set_enabled(enabled):
    config = load_config()
    config["enabled"] = enabled
    save_config(config)

def get_conv_state():
    try:
        with open(CONV_STATE_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

def set_conv_state(state):
    with open(CONV_STATE_FILE, "w") as f:
        f.write(state if state else "")

def clear_conv_state():
    if os.path.exists(CONV_STATE_FILE):
        os.remove(CONV_STATE_FILE)

def read_count():
    try:
        with open(COUNT_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def read_status():
    try:
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()
    except:
        return "No cycles run yet"

# ---------- Routes ----------
@app.route('/')
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"ok": True}), 200

        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]

        if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
            send_message(chat_id, "⛔ Unauthorised.")
            return jsonify({"ok": True}), 200

        text = msg.get("text", "").strip()

        if text.lower() == "/cancel":
            clear_conv_state()
            send_message(chat_id, "❌ Cancelled.")
            return jsonify({"ok": True}), 200

        if text == "/stop":
            config = load_config()
            if config["enabled"]:
                set_enabled(False)
                send_message(chat_id, "⏹️ Cycle stopped.")
            else:
                send_message(chat_id, "⏹️ Already stopped.")
            return jsonify({"ok": True}), 200

        if text == "/status":
            config = load_config()
            enabled = config["enabled"]
            count = read_count()
            last = read_status()
            send_message(chat_id,
                         f"🔄 *Status*\nEnabled: {'✅' if enabled else '❌'}\n"
                         f"Cycles completed: {count}\n"
                         f"Last cycle: {last}\n"
                         f"Title1: {config['vr_title1']}\n"
                         f"Title2: {config['vr_title2']}\n"
                         f"Announcement: {config['vr_announcement']}",
                         parse_mode="Markdown")
            return jsonify({"ok": True}), 200

        if text == "/start":
            state = get_conv_state()
            if state:
                send_message(chat_id, "Setup in progress. Send /cancel to abort.")
                return jsonify({"ok": True}), 200

            set_conv_state("waiting_title1")
            send_message(chat_id, "📝 Send **vr_title1**:", parse_mode="Markdown")
            return jsonify({"ok": True}), 200

        state = get_conv_state()
        if state:
            config = load_config()

            if state == "waiting_title1":
                config["vr_title1"] = text
                save_config(config)
                set_conv_state("waiting_title2")
                send_message(chat_id, "✅ Got it. Now send **vr_title2**:", parse_mode="Markdown")

            elif state == "waiting_title2":
                config["vr_title2"] = text
                save_config(config)
                set_conv_state("waiting_announcement")
                send_message(chat_id, "✅ Got it. Finally send **vr_announcement**:", parse_mode="Markdown")

            elif state == "waiting_announcement":
                config["vr_announcement"] = text
                config["enabled"] = True
                save_config(config)
                clear_conv_state()
                send_message(chat_id, "✅ All set! Cycle enabled.", parse_mode="Markdown")
            else:
                clear_conv_state()
                send_message(chat_id, "Error. Please /start again.")
            return jsonify({"ok": True}), 200

        send_message(chat_id, "Use /start, /stop, /status")
        return jsonify({"ok": True}), 200

    except Exception as e:
        return jsonify({"ok": False}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
