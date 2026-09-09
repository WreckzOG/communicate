import os
from openai import OpenAI
from anthropic import Anthropic

gpt = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
claude = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

CODEBOOK = """
Communicate v0.0.1 shared codebook:

G = GPT
C = Claude

F = From
T = To
I = Message ID
G = Goal
S = Current state
A = Action requested

H1 = Medieval Roblox house
D1 = Centered doorway on south wall
R1 = Build pitched roof
M1 = Stone
M2 = Dark wood
"""

packet = "C0|F:G|T:C|I:1|G:H1|S:walls,20x14,h8,D1,w4,M1|A:R1,M2"

claude_response = claude.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=300,
    system=f"""
You are participating in Communicate v0.0.1.

{CODEBOOK}

Decode incoming packets and respond with your understanding of the state
and the action you would take next.
""",
    messages=[
        {
            "role": "user",
            "content": packet
        }
    ]
)

print("GPT -> Claude")
print(packet)

print("\nClaude response:")
print(claude_response.content[0].text)
