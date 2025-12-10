from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return "Zendela Webhook Running", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook verification challenge
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification denied", 403

    if request.method == "POST":
        data = request.get_json()
        print("WEBHOOK EVENT:", data)

        # Handle incoming messages
        try:
            entry = data["entry"][0]
            messaging = entry["messaging"][0]
            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text", "")

                send_message(sender_id, f"You said: {text}")
        except Exception as e:
            print("Error handling event:", e)

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, params=params, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
