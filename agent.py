import random
from collections import deque
from config import *
from inference_engine import InferenceEngine

# =============================
# RANDOM AGENT
# =============================
class RandomAgent:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.pos = (0, 0)
        self.orientation = 'right'

    def choose_action(self):
        actions = [ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT,
                   ACTION_GRAB, ACTION_SHOOT, ACTION_CLIMB]
        return random.choice(actions)

    def update_kb(self, percepts, last_action):
        # RandomAgent không cần KB
        pass


# =============================
# HYBRID AGENT
# =============================
class HybridAgent:
    def __init__(self, size=GRID_SIZE, planning_algorithm='astar'):
        self.size = size
        self.pos = (0, 0)
        self.orientation = 'right'
        self.has_gold = False
        self.has_arrow = True
        self.planning_algorithm = planning_algorithm

        # KB: mỗi cell lưu visited, ok, wumpus, pit
        self.kb = [[{'visited': False, 'ok': False, 'wumpus': '?', 'pit': '?'} 
                    for _ in range(size)] for _ in range(size)]
        self.kb[0][0]['ok'] = True  # starting cell an toàn

        self.plan = deque()
        self.action_count = 0
        self.wumpus_alive_count = 1

        # Inference engine
        self.inference_engine = InferenceEngine(size)

    # -------- helper functions --------
    def _is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def _get_adjacent_cells(self, x, y):
        adjacent = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x+dx, y+dy
            if self._is_valid(nx, ny):
                adjacent.append((nx, ny))
        return adjacent

    def _turn_left(self, orientation):
        order = ['right','up','left','down']
        idx = order.index(orientation)
        return order[(idx+1)%4]

    def _turn_right(self, orientation):
        order = ['right','down','left','up']
        idx = order.index(orientation)
        return order[(idx+1)%4]

    def _handle_wumpus_movement_uncertainty(self):
        # Reset KB Wumpus khi nghi ngờ Wumpus di chuyển
        for y in range(self.size):
            for x in range(self.size):
                if self.kb[y][x]['wumpus'] != '?':
                    self.kb[y][x]['wumpus'] = '?'
                if self.kb[y][x]['ok'] and self.kb[y][x]['pit'] == 'no':
                    self.kb[y][x]['ok'] = False
        self.plan.clear()

    # -------- update KB --------
    def update_kb(self, percepts, last_action):
        # Cập nhật vị trí và hướng
        if last_action == ACTION_MOVE_FORWARD:
            dx, dy = DIRECTIONS[self.orientation]
            new_pos = (self.pos[0]+dx, self.pos[1]+dy)
            if self._is_valid(new_pos[0], new_pos[1]):
                self.pos = new_pos
        elif last_action == ACTION_TURN_LEFT:
            self.orientation = self._turn_left(self.orientation)
        elif last_action == ACTION_TURN_RIGHT:
            self.orientation = self._turn_right(self.orientation)
        elif last_action == ACTION_GRAB:
            self.has_gold = True
        elif last_action == ACTION_SHOOT:
            self.has_arrow = False

        x, y = self.pos
        self.kb[y][x]['visited'] = True
        self.kb[y][x]['ok'] = True

        self.action_count += 1
        if self.action_count % 5 == 0:
            self._handle_wumpus_movement_uncertainty()

        # Cập nhật neighbors theo percepts
        neighbors = self._get_adjacent_cells(x, y)
        if percepts['scream']:
            self.wumpus_alive_count -= 1
        if self.wumpus_alive_count == 0:
            for yy in range(self.size):
                for xx in range(self.size):
                    self.kb[yy][xx]['wumpus'] = 'no'
        elif percepts['stench']:
            for nx, ny in neighbors:
                if self.kb[ny][nx]['wumpus'] == '?':
                    self.kb[ny][nx]['wumpus'] = 'yes?'
        else:
            for nx, ny in neighbors:
                self.kb[ny][nx]['wumpus'] = 'no'

        if percepts['breeze']:
            for nx, ny in neighbors:
                if self.kb[ny][nx]['pit'] == '?':
                    self.kb[ny][nx]['pit'] = 'yes?'
        else:
            for nx, ny in neighbors:
                self.kb[ny][nx]['pit'] = 'no'

        # Đánh dấu safe nếu cả Wumpus và Pit đều 'no'
        for yy in range(self.size):
            for xx in range(self.size):
                if not self.kb[yy][xx]['ok']:
                    if self.kb[yy][xx]['wumpus']=='no' and self.kb[yy][xx]['pit']=='no':
                        self.kb[yy][xx]['ok'] = True

        # Cập nhật inference engine
        self.inference_engine.update_knowledge(self.pos, percepts)

    # -------- path planning skeleton --------
    def _find_path(self, start, goal):
        # Skeleton: trả về list of (x,y)
        if start == goal:
            return [start]
        if self.planning_algorithm == 'astar':
            # TODO: import / implement A*
            return [start, goal]
        else:
            # TODO: BFS
            return [start, goal]

    def _convert_path_to_actions(self, path):
        actions = deque()
        temp_orientation = self.orientation
        current_pos = self.pos
        for next_pos in path:
            dx = next_pos[0]-current_pos[0]
            dy = next_pos[1]-current_pos[1]

            # Xác định hướng cần đi
            if (dx, dy) == (1,0): req_orient='right'
            elif (dx, dy) == (-1,0): req_orient='left'
            elif (dx, dy) == (0,1): req_orient='up'
            elif (dx, dy) == (0,-1): req_orient='down'
            else: req_orient=temp_orientation  # fallback

            # Xoay đến hướng cần thiết
            while temp_orientation != req_orient:
                actions.append(ACTION_TURN_LEFT)
                temp_orientation = self._turn_left(temp_orientation)

            # Tiến 1 bước
            actions.append(ACTION_MOVE_FORWARD)
            current_pos = next_pos
        return actions

    # -------- choose action --------
    def choose_action(self):
        if self.plan:
            return self.plan.popleft()
        if self.has_gold and self.pos == (0,0):
            return ACTION_CLIMB
        if self.has_gold:
            path_home = self._find_path(self.pos, (0,0))
            self.plan = self._convert_path_to_actions(path_home)
            return self.plan.popleft() if self.plan else ACTION_MOVE_FORWARD

        # Tìm cell an toàn chưa thăm
        safe_unvisited = [(x,y) for y in range(self.size) for x in range(self.size)
                          if self.kb[y][x]['ok'] and not self.kb[y][x]['visited']]
        if safe_unvisited:
            # chọn target gần nhất
            target = min(safe_unvisited, key=lambda p: abs(p[0]-self.pos[0])+abs(p[1]-self.pos[1]))
            path = self._find_path(self.pos, target)
            self.plan = self._convert_path_to_actions(path)
            return self.plan.popleft() if self.plan else ACTION_MOVE_FORWARD

        # fallback: random safe action
        return random.choice([ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT])
