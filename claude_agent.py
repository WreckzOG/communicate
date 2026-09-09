import os
import subprocess

from anthropic import Anthropic
from workspace_tools import snapshot, apply_writes, extract_packet

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


SYSTEM = """
You are the Claude coding agent inside Communicate.

You collaborate with GPT on a shared project.

You receive:

1. A Communicate packet from GPT
2. A snapshot of the shared project workspace

You may modify files ONLY by outputting WRITE blocks.

Format:

WRITE:index.html
<complete contents>
ENDWRITE

WRITE:style.css
<complete contents>
ENDWRITE

You may write multiple files during one turn.

IMPORTANT:
- Inspect the existing workspace before making changes.
- Do not erase good work unnecessarily.
- Actually perform the requested task through WRITE blocks.
- Do not merely describe what should be changed.
- Keep the project functional.
- You and GPT share the exact same files.

When your turn is finished, output exactly ONE Communicate packet as
the final line.

Format:

C0|F:claude|T:gpt|P:E|S:<compact description of project state>|A:<what GPT should do next>

If the entire project is genuinely finished:

C0|F:claude|T:gpt|P:X|S:<final state>|A:stop

Communicate owns message IDs. Do not generate I fields.
"""


def receive():
    result = subprocess.run(
        ["python", "communicate.py", "receive", "claude"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def ask_claude(packet):
    workspace = snapshot()

    prompt = f"""
INCOMING COMMUNICATE PACKET:

{packet}

CURRENT SHARED WORKSPACE:

{workspace}

Perform your turn now.
"""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=8000,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text_parts = []

    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts).strip()


def route(packet):
    parts = packet.split("|")
    fields = {}

    for part in parts[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            fields[key] = value

    subprocess.run([
        "python",
        "communicate.py",
        "send",
        fields["F"],
        fields["T"],
        fields["P"],
        fields["S"],
        fields["A"]
    ])


packet = receive()

if packet == "NO_PACKET":
    print("[Claude] No packet waiting.")
    raise SystemExit

print("[Communicate -> Claude]")
print(packet)

response = ask_claude(packet)

print("\n[Claude]")
print(response)

written = apply_writes(response)

for filename in written:
    print(f"[Workspace] Claude wrote {filename}")

handoff = extract_packet(response)

if not handoff:
    print("[ERROR] Claude did not return a Communicate packet.")
    raise SystemExit(1)

route(handoff)

print("\n[Communicate] Claude handoff routed to GPT.")
