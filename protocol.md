# Communicate Protocol v0.0.1

Communicate transfers working state between LLMs using compact structured packets.

## Packet Format

C0|F:<from>|T:<to>|I:<id>|G:<goal>|S:<state>|A:<action>

## Fields

F = Sender  
T = Receiver  
I = Message ID  
G = Goal  
S = Current state  
A = Action expected from the receiver  

## Shared Codebook

Both models should load the same Communicate codebook before exchanging packets.

Recurring concepts should use short shared IDs.

Dynamic information should remain directly inside the packet.

Example codebook:

G = GPT  
C = Claude  

H1 = Medieval Roblox house  
D1 = Centered doorway on south wall  
R1 = Build pitched roof  
M1 = Stone  
M2 = Dark wood  

## Example Packet

C0|F:G|T:C|I:1|G:H1|S:walls,20x14,h8,D1,w4,M1|A:R1,M2

This means:

GPT is sending Claude message 1.

Goal:
Build a medieval Roblox house.

Current state:
- 20x14 footprint
- Walls complete
- Walls are 8 studs high
- Stone walls
- Centered 4-stud doorway on the south wall

Action:
Build a dark wooden pitched roof.

## Core Rule

The receiving model should be able to continue the task using only:

1. The shared Communicate codebook
2. The received packet

The original conversation should not be required.
