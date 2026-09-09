# Communicate Shared Codebook v0.0.1

This codebook defines shared symbols understood by all models participating in Communicate.

The codebook is loaded once before communication begins. Models should then exchange Communicate packets without redefining these symbols.

## Models

G = GPT
C = Claude

## Message Fields

F = From
T = To
I = Message ID
G = Goal
S = Current state
A = Action requested

## Message Types

Q = Question
R = Result
E = Error
X = Stop

## Roblox Test Vocabulary

H1 = Medieval Roblox house
D1 = Centered doorway on south wall
R1 = Build pitched roof
M1 = Stone
M2 = Dark wood

## Rules

1. Use shared symbols when a matching concept exists.
2. Keep changing values such as dimensions, counts, and coordinates directly in the packet.
3. Do not sacrifice necessary information merely to shorten a packet.
4. Use plain language when the codebook cannot represent something accurately.
5. Do not redefine an existing symbol during a conversation.
