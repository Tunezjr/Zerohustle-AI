import os
from flask import Flask, request
from twilio.rest import Client
from openai import OpenAI

app = Flask(__name__)

AGENT_NAME = "Zerohustle"
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
        model="anthropic/claude-sonnet-4-5",
        messages=[
            {"role": "system", "content": f"You are {AGENT_NAME}, an AI agent that polices language in other agents outputs."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return "Zerohustle is running", 200

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