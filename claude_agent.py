import os
import subprocess
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """
You are the Claude side of Communicate v0.0.1.

You receive compact packets from another AI agent.

Packet format:
C0|F:<from>|T:<to>|I:<id>|P:<phase>|S:<state>|A:<action>

Your job:
1. Decode the packet.
2. Perform or reason about the requested action.
3. When finished, produce exactly ONE final handoff packet.
4. The handoff packet must be addressed back to GPT.
5. Stop after producing the packet.

Your output MUST end with:

C0|F:claude|T:gpt|P:E|S:<updated state>|A:<next action>
"""

def receive():
    result = subprocess.run(
        ["python", "communicate.py", "receive", "claude"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def ask_claude(packet):
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": packet
            }
        ]
    )

    text_parts = []

    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts)

packet = receive()

if packet == "NO_PACKET":
    print("[Claude] No packet waiting.")
    raise SystemExit

print("[Communicate -> Claude]")
print(packet)

response = ask_claude(packet)

print("\n[Claude]")
print(response)

# Route Claude's final packet back through Communicate
if response.startswith("C0|"):
    parts = response.split("|")

    fields = {}

    for part in parts[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            fields[key] = value

    sender = fields.get("F")
    receiver = fields.get("T")
    phase = fields.get("P")
    state_text = fields.get("S")
    action = fields.get("A")

    subprocess.run([
        "python",
        "communicate.py",
        "send",
        sender,
        receiver,
        phase,
        state_text,
        action
    ])

    print("\n[Communicate] Claude handoff routed to GPT.")
