from http.server import BaseHTTPRequestHandler
import json
import anthropic
from twilio.rest import Client
from urllib.parse import parse_qs

AGENT_NAME = "Zerohustle"

ANTHROPIC_CLIENT = anthropic.Anthropic(
    api_key="YOUR_KEY"
)

TWILIO_ACCOUNT_SID = "YOUR_SID"
TWILIO_AUTH_TOKEN = "YOUR_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+16405002689"

twilio_client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)

def run_agent(user_message):
    response = ANTHROPIC_CLIENT.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=512,
        system=f"You are {AGENT_NAME}",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)

        incoming_msg = data.get("Body", [""])[0]
        sender = data.get("From", [""])[0]

        reply = run_agent(incoming_msg)

        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=reply,
            to=sender
        )

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
