import random
import numpy as np
from config import *

class WumpusWorld:
    def __init__(self, size=GRID_SIZE, pit_prob=PIT_PROBABILITY, num_wumpus=2, moving_wumpus=False):
        self.size = size
        self.pit_prob = pit_prob
        self.num_wumpus = num_wumpus
        self.moving_wumpus = moving_wumpus
        self.turn_count = 0

        self._generate_world()

        # Agent state
        self.agent_pos = (0, 0)
        self.agent_orientation = 'right'
        self.has_arrow = True
        self.has_gold = False
        self.score = 0
        self.game_over = False
        self.game_outcome = None

        # Transient percepts
        self.scream = False
        self.bump = False

    def _generate_world(self):
        """Generate pits, wumpus, and gold in a new random world."""
        self.grid = np.full((self.size, self.size), ' ', dtype=str)
        self.pit_pos = set()
        self.wumpus_positions = set()

        safe_zone = {(0,0), (1,0), (0,1)}

        # Place pits
        for r in range(self.size):
            for c in range(self.size):
                if (c, r) not in safe_zone and random.random() < self.pit_prob:
                    self.pit_pos.add((c, r))
                    self.grid[r, c] = 'P'

        # Place Wumpus
        while len(self.wumpus_positions) < self.num_wumpus:
            c = random.randint(0, self.size-1)
            r = random.randint(0, self.size-1)
            if (c, r) not in safe_zone and (c, r) not in self.pit_pos and (c, r) not in self.wumpus_positions:
                self.wumpus_positions.add((c, r))
                self.grid[r, c] = 'W'

        # Place gold
        while True:
            c = random.randint(0, self.size-1)
            r = random.randint(0, self.size-1)
            if (c, r) not in self.pit_pos and (c, r) not in self.wumpus_positions:
                self.gold_pos = (c, r)
                self.grid[r, c] = 'G'
                break

    def get_percepts(self):
        """Return percepts based on agent's current location."""
        x, y = self.agent_pos
        percepts = {
            'stench': False,
            'breeze': False,
            'glitter': (x, y) == self.gold_pos,
            'bump': self.bump,
            'scream': self.scream
        }

        # reset bump/scream each turn
        self.bump = False
        self.scream = False

        # Stench if adjacent to Wumpus
        for nx, ny in self._adjacent_cells(x, y):
            if (nx, ny) in self.wumpus_positions:
                percepts['stench'] = True
                break

        # Breeze if adjacent to Pit
        for nx, ny in self._adjacent_cells(x, y):
            if (nx, ny) in self.pit_pos:
                percepts['breeze'] = True
                break

        return percepts

    def _adjacent_cells(self, x, y):
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                yield nx, ny

    def execute_action(self, action):
        """Perform agent's chosen action."""
        if self.game_over:
            return

        self.score -= 1
        self.turn_count += 1

        if action == ACTION_MOVE_FORWARD:
            self._move_forward()
        elif action == ACTION_TURN_LEFT:
            self.agent_orientation = self._turn('left')
        elif action == ACTION_TURN_RIGHT:
            self.agent_orientation = self._turn('right')
        elif action == ACTION_GRAB:
            if self.agent_pos == self.gold_pos:
                self.has_gold = True
                self.gold_pos = None
                self.grid[self.agent_pos[1], self.agent_pos[0]] = ' '
        elif action == ACTION_SHOOT:
            if self.has_arrow:
                self.has_arrow = False
                self.score -= 10
                self._shoot_arrow()
        elif action == ACTION_CLIMB:
            if self.agent_pos == (0, 0):
                if self.has_gold:
                    self.score += 1000
                    self.game_outcome = "Victory (Gold)"
                else:
                    self.game_outcome = "Exit (No Gold)"
                self.game_over = True
                return

        # Check if agent dies
        if self.agent_pos in self.pit_pos or self.agent_pos in self.wumpus_positions:
            self.score -= 1000
            self.game_outcome = "Eaten/Fell"
            self.game_over = True
            return

        # Move Wumpus if enabled
        if self.moving_wumpus and self.turn_count % 5 == 0:
            self._move_all_wumpuses()

    def _move_forward(self):
        dx, dy = DIRECTIONS[self.agent_orientation]
        nx, ny = self.agent_pos[0] + dx, self.agent_pos[1] + dy
        if 0 <= nx < self.size and 0 <= ny < self.size:
            self.agent_pos = (nx, ny)
        else:
            self.bump = True

    def _turn(self, direction):
        orientations = ['up','right','down','left']
        idx = orientations.index(self.agent_orientation)
        if direction == 'left':
            return orientations[(idx - 1) % 4]
        else:
            return orientations[(idx + 1) % 4]

    def _shoot_arrow(self):
        dx, dy = DIRECTIONS[self.agent_orientation]
        x, y = self.agent_pos
        while 0 <= x < self.size and 0 <= y < self.size:
            x += dx
            y += dy
            if (x, y) in self.wumpus_positions:
                self.wumpus_positions.remove((x, y))
                self.scream = True
                break

    def _move_all_wumpuses(self):
        new_positions = set()
        for wx, wy in self.wumpus_positions:
            candidates = [(wx+dx, wy+dy) for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]
                          if 0 <= wx+dx < self.size and 0 <= wy+dy < self.size
                          and (wx+dx, wy+dy) not in self.pit_pos
                          and (wx+dx, wy+dy) != self.agent_pos
                          and (wx+dx, wy+dy) not in new_positions]
            if candidates:
                new_positions.add(random.choice(candidates))
            else:
                new_positions.add((wx, wy))
        self.wumpus_positions = new_positions

    def display_map(self, agent=None):
        """Show full map for debugging."""
        for r in reversed(range(self.size)):
            row_str = ""
            for c in range(self.size):
                if self.agent_pos == (c, r):
                    row_str += "A "
                elif (c, r) in self.pit_pos:
                    row_str += "P "
                elif (c, r) in self.wumpus_positions:
                    row_str += "W "
                elif (c, r) == self.gold_pos:
                    row_str += "G "
                else:
                    row_str += ". "
            print(row_str)
        print()
