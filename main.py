from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Zendela Webhook Running", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == "zendela_verify_123":
            return challenge, 200
        else:
            return "Verification failed", 403

    if request.method == "POST":
        print("Incoming webhook:", request.json)
        return "OK", 200
