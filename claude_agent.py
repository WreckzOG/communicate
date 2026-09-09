import os
import subprocess

from anthropic import Anthropic
from workspace_tools import snapshot, apply_writes, extract_packet


client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    timeout=300.0,
    max_retries=0
)


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
- Preserve existing good work.
- Make the SMALLEST change necessary to complete your task.
- Do NOT rewrite a file unless that file actually needs modification.
- Do NOT reproduce unchanged files.
- Avoid unnecessary prose.
- Keep output compact so all WRITE blocks can finish.
- Every WRITE block MUST end with ENDWRITE.
- You and GPT share the exact same files.

When your turn is complete:

1. Finish every WRITE block with ENDWRITE.
2. Output exactly ONE Communicate packet.
3. The packet MUST be the final line of your response.
4. Do not write anything after the packet.
5. Do not generate a message ID. Communicate owns message IDs.

Normal handoff format:

C0|F:claude|T:gpt|P:E|S:<compact description of project state>|A:<what GPT should do next>

If the entire project is genuinely complete:

C0|F:claude|T:gpt|P:X|S:<final state>|A:stop
"""


def receive():
    result = subprocess.run(
        ["python", "communicate.py", "receive", "claude"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()
from anthropic import Anthropic, APITimeoutError

def ask_claude(packet):
    workspace = snapshot()

    prompt = f"""
INCOMING COMMUNICATE PACKET:

{packet}

CURRENT SHARED WORKSPACE:

{workspace}

Perform your turn now.

Remember:
- Finish all WRITE blocks.
- Your FINAL LINE must be exactly one C0 Communicate packet.
"""

    print("[Claude] Sending request...", flush=True)

    try:
        message = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=16000,
            system=SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    except APITimeoutError:
        print("[Claude ERROR] API request timed out.", flush=True)
        return None

    print("[Claude] Response received.", flush=True)

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

    required = ["F", "T", "P", "S", "A"]

    missing = [key for key in required if not fields.get(key)]

    if missing:
        raise ValueError(
            f"Communicate packet missing required fields: {missing}"
        )

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


# Reliability fallback:
# If Claude successfully did work but forgot the final C0 packet,
# do not kill the entire Communicate session.
if not handoff:
    print(
        "[WARN] Claude omitted the Communicate handoff packet. "
        "Generating fallback."
    )

    if written:
        state_summary = "updated:" + ",".join(written)
    else:
        state_summary = "turn_completed_no_file_changes"

    handoff = (
        "C0|F:claude|T:gpt|P:E|"
        f"S:{state_summary}|"
        "A:review_claude_changes_and_continue"
    )


print("\n[Claude -> Communicate]")
print(handoff)


route(handoff)

print("\n[Communicate] Claude handoff routed to GPT.")
