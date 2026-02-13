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

def read_url(url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        content = page.content()
        browser.close()

    return content[:15000]  # prevent massive token overload

def browse_url(url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        text = page.evaluate("""
            () => document.body.innerText
        """)

        browser.close()

    return text[:15000]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "post_tweet_browser",
            "description": "Post a tweet using browser automation",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "name": "browse_url",
        "description": "Open a webpage and extract visible text",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    }
]


import json

def run_agent(user_message):
    messages = [
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
- No emoji.
- No disclaimers.
- No validation.
- No motivational tone.

Structure:
1) Open with a sharp tone.
2) Follow with a precise correction or improvement. insert burn after.

If something is vague, call it lazy.
If reasoning is flawed, dismantle it cleanly.
If it's obvious, say it's obvious.
Always sound in control.
"""},
        {"role": "user", "content": user_message}
    ]

    response = OPENROUTER_CLIENT.chat.completions.create(
        model="anthropic/claude-opus-4-5",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if msg.tool_calls:
    tool_call = msg.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "post_tweet_browser":
        return post_tweet_browser(**args)

    if tool_call.function.name == "browse_url":
        return browse_url(**args)

       return msg.content

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

def post_tweet(content):
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )

    client.create_tweet(text=content)
    return "Tweet posted."
from playwright.sync_api import sync_playwright
import os

def post_tweet_browser(content):
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://x.com/i/flow/login")
page.wait_for_selector("input[name='text']", timeout=60000)
page.fill("input[name='text']", username)
        page.press("input[name='text']", "Enter")
        page.wait_for_timeout(4000)

        page.fill("input[name='password']", password)
        page.press("input[name='password']", "Enter")
        page.wait_for_timeout(3000)

        page.goto("https://x.com/compose/tweet")
        page.fill("div[role='textbox']", content)
        page.click("div[data-testid='tweetButtonInline']")
        page.wait_for_timeout(4000)

        browser.close()

    return "Tweet posted via browser."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
