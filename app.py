python
import anthropic
import os
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

AGENT_NAME = "Zerohustle"
ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_KEY"))
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

tools = [
    {
        "name": "check_text",
        "description": "Checks if a piece of text violates language rules",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to check"}
            },
            "required": ["text"]
        }
    }
]

def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    while True:
        response = ANTHROPIC_CLIENT.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            system=f"You are {AGENT_NAME}, an AI agent that polices language in other agents' outputs.",
            tools=tools,
            messages=messages
        )
        if response.stop_reason == "tool_use":
            tool_result = "VIOLATION: aggressive sales language detected"
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": response.content[0].id, "content": tool_result}]})
        else:
            return response.content[0].text

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "")
    reply = run_agent(incoming_msg)
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=reply,
        to=sender
    )
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)