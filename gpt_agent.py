import os
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM = """
You are the GPT side of Communicate v0.0.1.

You receive compact packets from another AI agent.

Packet format:
C0|F:<from>|T:<to>|I:<id>|P:<phase>|S:<state>|A:<action>

Your job:
1. Decode the incoming packet.
2. Perform or reason about the requested action.
3. When your turn is complete, produce exactly ONE handoff packet.
4. Address the handoff to Claude.
5. Do not generate a message ID. Communicate owns message IDs.
6. Stop immediately after producing the packet.

Final output format:

C0|F:gpt|T:claude|P:E|S:<updated state>|A:<next action>
"""


def receive():
    result = subprocess.run(
        ["python", "communicate.py", "receive", "gpt"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def ask_gpt(packet):
    response = client.responses.create(
        model="gpt-5.6-sol",
        instructions=SYSTEM,
        input=packet
    )

    return response.output_text.strip()


def route_response(response):
    # Find the Communicate packet in case the model adds whitespace.
    packet = None

    for line in response.splitlines():
        line = line.strip()

        if line.startswith("C0|"):
            packet = line
            break

    if packet is None:
        print("[ERROR] GPT did not return a valid C0 packet.")
        return

    parts = packet.split("|")
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

    if not all([sender, receiver, phase, state_text, action]):
        print("[ERROR] GPT packet is missing required fields.")
        return

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

    print("\n[Communicate] GPT handoff routed to Claude.")


packet = receive()

if packet == "NO_PACKET":
    print("[GPT] No packet waiting.")
    raise SystemExit

print("[Communicate -> GPT]")
print(packet)

response = ask_gpt(packet)

print("\n[GPT]")
print(response)

route_response(response)
