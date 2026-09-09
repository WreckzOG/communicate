import os
import subprocess

from openai import OpenAI
from workspace_tools import snapshot, apply_writes, extract_packet

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=60.0,
    max_retries=0
)


SYSTEM = """
You are the GPT coding agent inside Communicate.

You collaborate with Claude on a shared project.

You receive:

1. A Communicate packet from Claude
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
- You and Claude share the exact same files.

When your turn is finished, output exactly ONE Communicate packet as
the final line.

Format:

C0|F:gpt|T:claude|P:E|S:<compact description of project state>|A:<what Claude should do next>

If the entire project is genuinely finished:

C0|F:gpt|T:claude|P:X|S:<final state>|A:stop

Communicate owns message IDs. Do not generate I fields.
"""


def receive():
    result = subprocess.run(
        ["python", "communicate.py", "receive", "gpt"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def ask_gpt(packet):
    workspace = snapshot()

    prompt = f"""
INCOMING COMMUNICATE PACKET:

{packet}

CURRENT SHARED WORKSPACE:

{workspace}

Perform your turn now.
"""

    print("[GPT] Sending request to OpenAI...", flush=True)

    try:
        response = client.responses.create(
            model="gpt-5.6-sol",
            instructions=SYSTEM,
            input=prompt
        )
    except Exception as e:
        print(f"[GPT ERROR] {type(e).__name__}: {e}", flush=True)
        raise

    print("[GPT] Response received.", flush=True)

    return response.output_text.strip()


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
    print("[GPT] No packet waiting.")
    raise SystemExit

print("[Communicate -> GPT]")
print(packet)

response = ask_gpt(packet)

print("\n[GPT]")
print(response)

written = apply_writes(response)

for filename in written:
    print(f"[Workspace] GPT wrote {filename}")

handoff = extract_packet(response)

if not handoff:
    print("[ERROR] GPT did not return a Communicate packet.")
    raise SystemExit(1)

route(handoff)

print("\n[Communicate] GPT handoff routed to Claude.")
