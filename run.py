import subprocess
import json
import time

MAX_TURNS = 4


def get_current_agent():
    with open("state.json", "r") as f:
        state = json.load(f)

    return state["current_agent"]


def run_agent(agent):
    if agent == "gpt":
        script = "gpt_agent.py"
    elif agent == "claude":
        script = "claude_agent.py"
    else:
        print(f"[Communicate] Unknown agent: {agent}")
        return False

    print(f"\n========== {agent.upper()} TURN ==========\n")

    result = subprocess.run(["python", script])

    return result.returncode == 0


print("""
================================
       COMMUNICATE v0.0.1
================================
""")

for turn in range(MAX_TURNS):

    agent = get_current_agent()

    if agent is None:
        print("[Communicate] No active agent.")
        break

    print(f"[Communicate] Turn {turn + 1}/{MAX_TURNS}")
    print(f"[Communicate] Waking {agent}...")

    success = run_agent(agent)

    if not success:
        print(f"[Communicate] {agent} failed.")
        break

    time.sleep(1)

print("\n[Communicate] Session ended.")
