python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

AGENT_NAME = "Tunez"

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

messages = [{"role": "user", "content": "Check this text: 'Buy now or you'll regret it!'"}]

while True:
    response = client.messages.create(
        model="claude-opus-4-5-20250929",
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
        print(response.content[0].text)
        break