import random
<<<<<<< HEAD
from config import *

class WumpusWorld:
    def __init__(self, size=GRID_SIZE, pit_prob=PIT_PROBABILITY):
        self.size = size
        self.pit_prob = pit_prob
        self.score = 0
        self.game_over = False
        self.game_outcome = ""
        self.action_count = 0

        # Grid: ' ' = empty, 'P' = pit, 'W' = Wumpus, 'G' = gold
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.pit_pos = []
        self.wumpus_positions = []
        self.gold_pos = None

        self.agent_pos = (0, 0)
        self.agent_orientation = 'right'
        self.agent_has_gold = False
        self.agent_has_arrow = True

        self._generate_pits()
        self._generate_wumpus()
        self._generate_gold()
    
    # ----------------- World Generation -----------------
    def _generate_pits(self):
        for r in range(self.size):
            for c in range(self.size):
                if (c, r) == (0, 0):
                    continue
                if random.random() < self.pit_prob:
                    self.grid[r][c] = 'P'
                    self.pit_pos.append((c, r))

    def _generate_wumpus(self):
        count = 0
        while count < MAX_WUMPUS:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.grid[y][x] == ' ' and (x, y) != (0, 0):
                self.grid[y][x] = 'W'
                self.wumpus_positions.append((x, y))
                count += 1

    def _generate_gold(self):
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.grid[y][x] == ' ':
                self.grid[y][x] = 'G'
                self.gold_pos = (x, y)
                break

    # ----------------- Percepts -----------------
    def get_percepts(self):
=======
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
>>>>>>> e7fe1e6fdaf35efcce847828f74d9284fc8197a8
        x, y = self.agent_pos
        percepts = {
            'stench': False,
            'breeze': False,
<<<<<<< HEAD
            'glitter': False,
            'bump': False,
            'scream': False
        }

        # Adjacent cells
        neighbors = self._get_adjacent_cells(x, y)
        for nx, ny in neighbors:
            if self.grid[ny][nx] == 'W':
                percepts['stench'] = True
            if self.grid[ny][nx] == 'P':
                percepts['breeze'] = True
        # Current cell
        if self.grid[y][x] == 'G':
            percepts['glitter'] = True

        return percepts

    # ----------------- Action Execution -----------------
    def _get_adjacent_cells(self, x, y):
        cells = []
        for dx, dy in DIRECTIONS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                cells.append((nx, ny))
        return cells

    def execute_action(self, action):
        if self.game_over:
            return

        self.action_count += 1
        reward = 0
        x, y = self.agent_pos

        if action == ACTION_MOVE_FORWARD:
            dx, dy = DIRECTIONS[self.agent_orientation]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self.agent_pos = (nx, ny)
                reward += MOVE_COST
                # Check death
                if self.grid[ny][nx] == 'P':
                    reward += DEATH_PENALTY
                    self.game_over = True
                    self.game_outcome = "Fell into a pit!"
                elif self.grid[ny][nx] == 'W':
                    reward += DEATH_PENALTY
                    self.game_over = True
                    self.game_outcome = "Eaten by Wumpus!"
            else:
                reward += MOVE_COST  # bump cost
        elif action == ACTION_TURN_LEFT or action == ACTION_TURN_RIGHT:
            reward += TURN_COST
            self._turn(action)
        elif action == ACTION_GRAB:
            if self.agent_pos == self.gold_pos and not self.agent_has_gold:
                self.agent_has_gold = True
                reward += GOLD_REWARD
                self.grid[y][x] = ' '  # remove gold
        elif action == ACTION_SHOOT:
            if self.agent_has_arrow:
                self.agent_has_arrow = False
                reward += SHOOT_COST
                if self._shoot_arrow():
                    reward += 0  # can add extra reward if desired
        elif action == ACTION_CLIMB:
            if self.agent_pos == (0, 0):
                self.game_over = True
                if self.agent_has_gold:
                    reward += CLIMB_REWARD
                    self.game_outcome = "Escaped with gold!"
                else:
                    reward += CLIMB_NO_GOLD
                    self.game_outcome = "Escaped without gold!"
            else:
                reward += 0  # cannot climb outside (ignored)

        self.score += reward

        # Move Wumpus every WUMPUS_MOVE_INTERVAL actions
        if self.action_count % WUMPUS_MOVE_INTERVAL == 0:
            self._move_wumpus()

    def _turn(self, action):
        orientations = ['up', 'right', 'down', 'left']
        idx = orientations.index(self.agent_orientation)
        if action == ACTION_TURN_LEFT:
            self.agent_orientation = orientations[(idx - 1) % 4]
        else:
            self.agent_orientation = orientations[(idx + 1) % 4]

    def _shoot_arrow(self):
        # shoot straight in current orientation until hitting Wumpus or wall
        x, y = self.agent_pos
        dx, dy = DIRECTIONS[self.agent_orientation]
        while 0 <= x < self.size and 0 <= y < self.size:
            x += dx
            y += dy
            if not (0 <= x < self.size and 0 <= y < self.size):
                break
            if self.grid[y][x] == 'W':
                self.grid[y][x] = ' '
                self.wumpus_positions.remove((x, y))
                return True  # scream emitted
        return False
    
    # ----------------- Moving Wumpus -----------------
    def _move_wumpus(self):
        new_positions = []
        for wx, wy in self.wumpus_positions:
            neighbors = self._get_adjacent_cells(wx, wy)
            random.shuffle(neighbors)
            moved = False
            for nx, ny in neighbors:
                if self.grid[ny][nx] in [' ', 'G']:  # valid move
                    # check collision with agent
                    if (nx, ny) == self.agent_pos:
                        self.score += DEATH_PENALTY
                        self.game_over = True
                        self.game_outcome = "Wumpus moved into agent!"
                        return
                    self.grid[wy][wx] = ' '
                    self.grid[ny][nx] = 'W'
                    new_positions.append((nx, ny))
                    moved = True
                    break
            if not moved:
                new_positions.append((wx, wy))
        self.wumpus_positions = new_positions
=======
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
>>>>>>> e7fe1e6fdaf35efcce847828f74d9284fc8197a8
