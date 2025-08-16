import random
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
        x, y = self.agent_pos
        percepts = {
            'stench': False,
            'breeze': False,
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
