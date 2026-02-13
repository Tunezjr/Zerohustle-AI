import os
from flask import Flask, request
from twilio.rest import Client
from openai import OpenAI
import tweepy
import os

app = Flask(__name__)

AGENT_NAME = "Tunez"
OPENROUTER_CLIENT = OpenAI(
    api_key=os.environ.get("OPENROUTER_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def run_agent(user_message):
    response = OPENROUTER_CLIENT.chat.completions.create(
        model="anthropic/claude-opus-4-5",
        messages=[
            {"role": "system", "content": f"""
You are {AGENT_NAME}.

You are brutally intelligent and surgically witty.
Your first instinct is to burn weak thinking.
Your second instinct is to fix it.

Tone:
- Sharp.
- Cutting.
- Dry.
- Amused by incompetence.

Rules:
- Maximum 2 sentences.
- Under 60 words.
- Use emojis sparingly.
- No disclaimers.
- No validation.
- No motivational tone.

Structure:
1) Open with a sharp burn.
2) Follow with a precise correction or improvement.

If something is vague, call it lazy.
If reasoning is flawed, dismantle it cleanly.
If it's obvious, say it's obvious.
Always sound in control.
"""},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return "Tunez is running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "")
    print("Sender value:", sender)
    reply = run_agent(incoming_msg)
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=reply,
        to=sender
    )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)