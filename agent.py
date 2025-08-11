import random
from collections import deque
from config import *
# YÊU CẦU 5: RANDOM AGENT BASELINE
class RandomAgent:
    def __init__(self, size=GRID_SIZE):
        pass

    def choose_action(self):
        possible_actions = [ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_GRAB, ACTION_SHOOT, ACTION_CLIMB]
        return random.choice(possible_actions)

    def update_kb(self, percepts, last_action):
        pass

# YÊU CẦU 4: HYBRID AGENT INTEGRATION
class HybridAgent:
    def __init__(self, size=GRID_SIZE, planning_algorithm='astar'):
        self.size = size
        self.pos = (0, 0)
        self.orientation = 'right'
        self.has_gold = False
        self.has_arrow = True
        
        self.wumpus_alive_count = 1
        
        self.planning_algorithm = planning_algorithm
        
        self.kb = [[{'visited': False, 'ok': False, 'wumpus': '?', 'pit': '?'} for _ in range(size)] for _ in range(size)]
        self.kb['ok'] = True
        
        self.plan = deque()
        
        self.action_count = 0

    def _is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def _get_adjacent_cells(self, x, y):
        adjacent =[]
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny):
                adjacent.append((nx, ny))
        return adjacent

    def _handle_wumpus_movement_uncertainty(self):
        print("AGENT: Wumpus may have moved. Resetting Wumpus knowledge.")
        for r in range(self.size):
            for c in range(self.size):
                if self.kb[r][c]['wumpus']!= '?':
                    self.kb[r][c]['wumpus'] = '?'
                
                if self.kb[r][c]['ok'] and self.kb[r][c]['pit'] == 'no':
                     self.kb[r][c]['ok'] = False

    def update_kb(self, percepts, last_action):
        if last_action == ACTION_MOVE_FORWARD:
            dx, dy = DIRECTIONS[self.orientation]
            new_pos = (self.pos + dx, self.pos[1] + dy)
            if self._is_valid(new_pos, new_pos[1]):
                self.pos = new_pos
        elif last_action == ACTION_TURN_LEFT:
            orientations = ['right', 'up', 'left', 'down']
            idx = orientations.index(self.orientation)
            self.orientation = orientations[(idx + 1) % 4]
        elif last_action == ACTION_TURN_RIGHT:
            orientations = ['right', 'down', 'left', 'up']
            idx = orientations.index(self.orientation)
            self.orientation = orientations[(idx + 1) % 4]
        elif last_action == ACTION_GRAB:
            self.has_gold = True
        elif last_action == ACTION_SHOOT:
            self.has_arrow = False
        
        x, y = self.pos
        self.kb[x][y]['visited'] = True
        self.kb[x][y]['ok'] = True 
        self.action_count += 1
        if self.action_count % 5 == 0:
            self._handle_wumpus_movement_uncertainty()
            self.plan.clear()

        neighbors = self._get_adjacent_cells(x, y)
        
        if percepts['scream']:
            self.wumpus_alive_count -= 1
        
        if self.wumpus_alive_count == 0:
            for r in range(self.size):
                for c in range(self.size): self.kb[r][c]['wumpus'] = 'no'
        elif percepts['stench']:
            for nx, ny in neighbors:
                if self.kb[nx][ny]['wumpus'] == '?': self.kb[nx][ny]['wumpus'] = 'yes?'
        else:
            for nx, ny in neighbors: self.kb[nx][ny]['wumpus'] = 'no'

        if percepts['scream']:
            self.wumpus_alive = False
        
        if not self.wumpus_alive:
            for r in range(self.size):
                for c in range(self.size):
                    self.kb[r][c]['wumpus'] = 'no'
        elif percepts['stench']:
            for nx, ny in neighbors:
                if self.kb[nx][ny]['wumpus'] == '?':
                    self.kb[nx][ny]['wumpus'] = 'yes?'
        else:
            for nx, ny in neighbors:
                self.kb[nx][ny]['wumpus'] = 'no'

        if percepts['breeze']:
            for nx, ny in neighbors:
                if self.kb[nx][ny]['pit'] == '?':
                    self.kb[nx][ny]['pit'] = 'yes?'
        else:
            for nx, ny in neighbors:
                self.kb[nx][ny]['pit'] = 'no'
        for r in range(self.size):
            for c in range(self.size):
                if not self.kb[r][c]['ok']:
                    if self.kb[r][c]['wumpus'] == 'no' and self.kb[r][c]['pit'] == 'no':
                        self.kb[r][c]['ok'] = True
    def _find_path(self, start, goal):
        if start == goal:
            return
        
        if self.planning_algorithm == 'astar':
            astar_solver=find_path_astar(start, goal, self.kb, self._get_adjacent_cells)
            return astar_solver
        elif self.planning_algorithm == 'bfs':
            bfs_solver=find_path_bfs(start, goal, self.kb, self._get_adjacent_cells)
            return bfs_solver
        else:
            print(f"Warning: Unknown algorithm '{self.planning_algorithm}'. Defaulting to BFS.")
            return find_path_bfs(start, goal, self.kb, self._get_adjacent_cells)

    def _convert_path_to_actions(self, path):
        """Chuyển đổi một chuỗi tọa độ thành một chuỗi hành động."""
        actions = deque()
        temp_orientation = self.orientation
        current_pos = self.pos

        for next_pos in path:
            dx, dy = next_pos - current_pos, next_pos[1] - current_pos[1]
            required_orientation = ''
            if (dx, dy) == (1, 0): required_orientation = 'right'
            elif (dx, dy) == (-1, 0): required_orientation = 'left'
            elif (dx, dy) == (0, 1): required_orientation = 'down'
            elif (dx, dy) == (0, -1): required_orientation = 'up'
            while temp_orientation!= required_orientation:
                actions.append(ACTION_TURN_LEFT)
                orientations = ['right', 'up', 'left', 'down']
                idx = orientations.index(temp_orientation)
                temp_orientation = orientations[(idx + 1) % 4]
            
            actions.append(ACTION_MOVE_FORWARD)
            current_pos = next_pos
        return actions

    def choose_action(self):
        if self.plan:
            return self.plan.popleft()
        if self.has_gold and self.pos == (0, 0):
            return ACTION_CLIMB
        if self.has_gold:
            path_to_home = self._find_path_bfs(self.pos, (0, 0))
            if path_to_home:
                self.plan = self._convert_path_to_actions(path_to_home)
                return self.plan.popleft()
        safe_unvisited = []
        for r in range(self.size):
            for c in range(self.size):
                if self.kb[r][c]['ok'] and not self.kb[r][c]['visited']:
                    safe_unvisited.append((r, c))
        if safe_unvisited:
            target = min(safe_unvisited, key=lambda p: abs(p-self.pos) + abs(p[1]-self.pos[1]))
            path_to_target = self._find_path_bfs(self.pos, target)
            if path_to_target:
                self.plan = self._convert_path_to_actions(path_to_target)
                return self.plan.popleft()
        path_to_home = self._find_path_bfs(self.pos, (0, 0))
        if path_to_home:
            self.plan = self._convert_path_to_actions(path_to_home)
            self.plan.append(ACTION_CLIMB)
            return self.plan.popleft()
        return random.choice()