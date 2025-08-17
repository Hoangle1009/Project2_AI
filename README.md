Wumpus World Project

1. Environment Setup

Requires Python >= 3.9

2. Run Demo
The project supports two types of agents:

Hybrid Agent → Uses A* and BFS to find the optimal path.

Random Agent → Chooses actions randomly, without an optimal strategy.

To run the demo, use the command:

python main.py


3. Result Description

Hybrid Agent: Moves strategically, finds the optimal path using A*, switches to BFS when needed, and avoids dangers.

Random Agent: Chooses random moves, which may lead to wandering paths or falling into pits.
