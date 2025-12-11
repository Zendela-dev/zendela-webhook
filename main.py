import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN", "zendela_verify_123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")


@app.route("/", methods=["GET"])
def index():
    return "Zendela Webhook Running", 200


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification request from Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # POST: incoming messages / events
    data = request.get_json()
    print("WEBHOOK EVENT:", data)

    if "entry" in data:
        for entry in data["entry"]:
            events = entry.get("messaging", []) or entry.get("standby", [])
            for event in events:
                handle_event(event)

    return "EVENT_RECEIVED", 200


def handle_event(event: dict) -> None:
    """
    Handles a single messaging event from FB or IG.
    """
    sender = event.get("sender", {})
    sender_id = sender.get("id")
    if not sender_id:
        return

    # Ignore delivery / read receipts etc.
    if "message" not in event:
        return

    message = event["message"]
    text = message.get("text", "")

    if not text:
        return

    route_message(sender_id, text)


def route_message(sender_id: str, text: str) -> None:
    """
    Very simple keyword router. You can expand this later.
    """
    t = text.strip().lower()

    if "demo" in t:
        # DEMO menu
        reply = (
            "Thanks for checking out the Zendela demo 👋\n"
            "Here’s how this works:\n\n"
            "1️⃣ Book a free Automation Audit\n"
            "2️⃣ See examples of what we automate\n"
            "3️⃣ Talk to a human\n\n"
            "Reply with 1, 2, or 3."
        )
        send_message(sender_id, reply)
        return

    if t == "1":
        reply = (
            "📅 Book your free Automation Audit here:\n"
            "https://zendela.us/#audit\n\n"
            "We’ll quickly identify your biggest bottlenecks and show what can be "
            "automated in your business."
        )
        send_message(sender_id, reply)
        return

    if t == "2":
        reply = (
            "🧩 Here’s what Zendela can automate for service businesses:\n"
            "- Missed calls → instant text-back\n"
            "- DM & form follow-up\n"
            "- Booking flows & reminders\n"
            "- Rebooking & review campaigns\n"
            "- Reporting & ROI tracking\n\n"
            "Full overview:\nhttps://zendela.us/#automate"
        )
        send_message(sender_id, reply)
        return

    if t == "3":
        reply = (
            "👤 No problem — I’ll jump in personally.\n"
            "Reply with a quick summary of your business and what you’d like to improve."
        )
        send_message(sender_id, reply)
        return

    # Default fallback
    default_reply = (
        "Hey, this is Zendela 👋\n"
        "We build automations that turn missed calls, DMs and manual follow-ups "
        "into booked revenue.\n\n"
        "Reply with:\n"
        "• DEMO – to see the interactive menu\n"
        "• 1 – to book a free Automation Audit\n"
        "• 2 – to see what we automate\n"
        "• 3 – to talk to a human"
    )
    send_message(sender_id, default_reply)


def send_message(recipient_id: str, text: str) -> None:
    """
    Sends a text message via the Meta Send API.
    Works for both Facebook Page and IG DMs (Messenger API for IG).
    """
    if not PAGE_ACCESS_TOKEN:
        print("ERROR: PAGE_ACCESS_TOKEN not set")
        return

    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }

    try:
        r = requests.post(url, params=params, json=payload, timeout=10)
        print("Send response:", r.status_code, r.text)
    except Exception as e:
        print("Error sending message:", e)


if __name__ == "__main__":
    # For local dev; Render will use gunicorn with PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
