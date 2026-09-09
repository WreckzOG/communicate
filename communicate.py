import json
import os
import sys
from datetime import datetime

STATE_FILE = "state.json"
INBOX_DIR = "inboxes"


def ensure_setup():
    os.makedirs(INBOX_DIR, exist_ok=True)

    if not os.path.exists(STATE_FILE):
        save_state({
            "current_agent": None,
            "message_id": 0,
            "status": "idle",
            "last_packet": None
        })

    for agent in ["gpt", "claude"]:
        path = os.path.join(INBOX_DIR, f"{agent}.jsonl")
        if not os.path.exists(path):
            open(path, "a").close()


def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_packet(sender, receiver, phase, state_text, action):
    state = load_state()
    message_id = state["message_id"] + 1

    packet = (
        f"C0|F:{sender}|T:{receiver}|I:{message_id}|"
        f"P:{phase}|S:{state_text}|A:{action}"
    )

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "packet": packet
    }

    inbox_path = os.path.join(INBOX_DIR, f"{receiver}.jsonl")

    with open(inbox_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    state["current_agent"] = receiver
    state["message_id"] = message_id
    state["status"] = "waiting"
    state["last_packet"] = packet

    save_state(state)

    print(packet)


def receive_packet(agent):
    inbox_path = os.path.join(INBOX_DIR, f"{agent}.jsonl")

    with open(inbox_path, "r") as f:
        lines = f.readlines()

    if not lines:
        print("NO_PACKET")
        return

    latest = json.loads(lines[-1])
    print(latest["packet"])


def show_state():
    print(json.dumps(load_state(), indent=2))


def main():
    ensure_setup()

    if len(sys.argv) < 2:
        print("""
Usage:

Send:
python communicate.py send <from> <to> <phase> "<state>" "<action>"

Receive:
python communicate.py receive <agent>

State:
python communicate.py state
""")
        return

    command = sys.argv[1]

    if command == "send":
        sender = sys.argv[2]
        receiver = sys.argv[3]
        phase = sys.argv[4]
        state_text = sys.argv[5]
        action = sys.argv[6]

        send_packet(
            sender,
            receiver,
            phase,
            state_text,
            action
        )

    elif command == "receive":
        receive_packet(sys.argv[2])

    elif command == "state":
        show_state()


if __name__ == "__main__":
    main()
