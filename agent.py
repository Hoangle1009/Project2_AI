import random
from collections import deque
from config import *
from inference_engine import InferenceEngine
from planning_module import bfs_path, astar_path, astar_path_to_risk, bfs_path_to_risk

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
        pass


class HybridAgent:
    def __init__(self, size=GRID_SIZE, planning_algorithm='astar'):
        self.size = size
        self.pos = (0,0)
        self.orientation = 'right'
        self.has_gold = False
        self.has_arrow = True
        self.planning_algorithm = planning_algorithm
        print(f"[DEBUG] Hybrid Agent initialized with planning algorithm: {self.planning_algorithm}")
        self.safe_cells = {(0,0)}
        self.kb = [[{'visited': False, 'ok': False, 'wumpus':'?', 'pit':'?', 'glitter':False} 
                    for _ in range(size)] for _ in range(size)]
        self.kb[0][0]['ok'] = True

        self.plan = deque()
        self.action_log = []
        self.inference_engine = InferenceEngine(size)
        self.awaiting_scream = None

    def _is_valid(self,x,y):
        return 0<=x<self.size and 0<=y<self.size

    def _get_adjacent(self,x,y):
        adj=[]
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx,ny=x+dx,y+dy
            if self._is_valid(nx,ny):
                adj.append((nx,ny))
        return adj

    def _turn_left(self, ori):
        order=['right','up','left','down']
        idx=order.index(ori)
        return order[(idx+1)%4]

    def _turn_right(self, ori):
        order=['right','down','left','up']
        idx=order.index(ori)
        return order[(idx+1)%4]

    def _print_safe_cells(self):
        safe_list = sorted(list(self.safe_cells))
        print(f"[DEBUG] Safe cells ({len(safe_list)}): {safe_list}")
    def update_kb(self, percepts, last_action):
        x, y = self.pos
        print("\n--- DEBUG SAFE CELLS ---")
        self._print_safe_cells()
        if self.awaiting_scream:
            dx, dy = self.awaiting_scream
            wx, wy = x + dx, y + dy

            if percepts.get('scream', False):

                print(f"=== Wumpus at ({wx}, {wy}) has been killed! ===")
                while self._is_valid(wx, wy):
                    if self.kb[wy][wx]['wumpus'] in ['yes', 'yes?']:
                        self.kb[wy][wx]['wumpus'] = 'no'
                        self.safe_cells.add((wx, wy))
                        path = self._find_path(self.pos, (wx, wy))
                        if path:
                            self.plan = self._path_to_actions(path)
                        for nx, ny in self._get_adjacent(wx, wy):
                            if self._is_valid(nx, ny):
                                self.kb[ny][nx]['wumpus'] = 'no'
                                self.safe_cells.add((nx, ny))
                        break
                    wx += dx
                    wy += dy
            else:
                print(f"=== No scream at ({wx}, {wy}), Wumpus still alive ===")
                
                while self._is_valid(wx, wy):
                    self.kb[wy][wx]['wumpus'] = 'no'
                    self.safe_cells.add((wx, wy))
                    wx += dx
                    wy += dy
                self.safe_cells.add((wx, wy))
                path = self._find_path(self.pos, (wx, wy))
                

        elif last_action==ACTION_MOVE_FORWARD:
            dx,dy=DIRECTIONS[self.orientation]
            nx,ny=self.pos[0]+dx,self.pos[1]+dy
            if self._is_valid(nx,ny):
                self.pos=(nx,ny)
        elif last_action==ACTION_TURN_LEFT:
            self.orientation=self._turn_left(self.orientation)
        elif last_action==ACTION_TURN_RIGHT:
            self.orientation=self._turn_right(self.orientation)
        elif last_action==ACTION_GRAB:
            self.has_gold=True

        x,y=self.pos
        self.kb[y][x]['visited']=True
        self.kb[y][x]['ok']=True
        if percepts.get('glitter',False):
            self.kb[y][x]['glitter']=True

        neighbors=self._get_adjacent(x,y)
        if percepts.get('breeze',False):
            for nx,ny in neighbors:
                if self.kb[ny][nx]['pit']=='?':
                    self.kb[ny][nx]['pit']='yes?'
        else:
            for nx,ny in neighbors:
                self.kb[ny][nx]['pit']='no'

        if percepts.get('stench',False):
            for nx,ny in neighbors:
                if self.kb[ny][nx]['wumpus']=='?':
                    self.kb[ny][nx]['wumpus']='yes?'
        else:
            for nx,ny in neighbors:
                self.kb[ny][nx]['wumpus']='no'

        for yy in range(self.size):
            for xx in range(self.size):
                if self.kb[yy][xx]['wumpus']=='no' and self.kb[yy][xx]['pit']=='no':
                    self.kb[yy][xx]['ok']=True
                    self.safe_cells.add((xx,yy))

  
        self.inference_engine.update_knowledge(self.pos, percepts)

    def _find_path(self,start,goal):
        if start==goal:
            return [start]
        if self.planning_algorithm=='astar':
            path=astar_path(start,goal,self.safe_cells,self.size)
        else:
            path=bfs_path(start,goal,self.safe_cells,self.size)
        return path
    def _find_risk_path(self,start,goal):
        if start==goal:
            return [start]
        if self.planning_algorithm=='astar':
            path=astar_path_to_risk(start,goal,self.safe_cells,self.size)
        else:
            path=bfs_path_to_risk(start,goal,self.safe_cells,self.size)
        return path

    def _path_to_actions(self,path):
        actions=deque()
        ori=self.orientation
        dir_map={(1,0):'right',(-1,0):'left',(0,1):'up',(0,-1):'down'}
        left_turn={'up':'left','left':'down','down':'right','right':'up'}
        right_turn={v:k for k,v in left_turn.items()}

        pos=self.pos
        for nxt in path[1:]:
            dx,dy=nxt[0]-pos[0], nxt[1]-pos[1]
            target_ori=dir_map[(dx,dy)]

            while ori!=target_ori:
                if left_turn[ori]==target_ori:
                    actions.append(ACTION_TURN_LEFT)
                    ori=left_turn[ori]
                else:
                    actions.append(ACTION_TURN_RIGHT)
                    ori=right_turn[ori]

            actions.append(ACTION_MOVE_FORWARD)
            pos=nxt
        return actions

    def _calculate_risk_cell(self, x, y):
        risk = 0
        if self.kb[y][x]['pit'] in ['yes','yes?']:
            risk += 0.5
        if self.kb[y][x]['wumpus'] in ['yes','yes?'] and self.has_arrow:
            risk += 0.5
        return risk

    def _get_least_risk_cell(self):
        min_risk = 1.1
        candidates = []

        neighbor_cells = set()
        for sx, sy in self.safe_cells:
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    neighbor_cells.add((nx, ny))

        for nx, ny in neighbor_cells:
            cell = self.kb[ny][nx]
            if not cell['visited'] and (nx, ny) not in self.safe_cells:
                r = self._calculate_risk_cell(nx, ny)
                if r < min_risk:
                    min_risk = r
                    candidates = [(nx, ny)]
                elif r == min_risk:
                    candidates.append((nx, ny))

        if candidates:
            chosen = random.choice(candidates)
            print(f"[DEBUG] Chọn risk cell {chosen} với risk={min_risk}")
            return chosen
        else:
            print("[DEBUG] Không còn risk cell lân cận của safe cells.")
            return None

    def _decide_shoot(self):
        if not self.has_arrow or self.awaiting_scream:
            return None

        x, y = self.pos
        dx, dy = DIRECTIONS[self.orientation]
        nx, ny = x + dx, y + dy

        while self._is_valid(nx, ny):
            if self.kb[ny][nx]['wumpus'] == 'yes?':
                self.awaiting_scream = (dx, dy)
                return ACTION_SHOOT
            nx += dx
            ny += dy

        return None

    def choose_action(self):
        if self.awaiting_scream:
            self.action_log.append("WaitingForScream")
            self.awaiting_scream = None
            return None

        if self.plan:
            action = self.plan.popleft()

        elif not self.has_gold and self.kb[self.pos[1]][self.pos[0]].get('glitter', False):
            action = ACTION_GRAB

        elif self.has_gold:
            if self.pos == (0, 0):
                action = ACTION_CLIMB
            else:
                if not self.plan:
                    path = self._find_path(self.pos, (0,0))
                    if path:
                        self.plan = self._path_to_actions(path)
                action = self.plan.popleft() if self.plan else random.choice(
                    [ACTION_MOVE_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT]
                )

        else:
            safe_unvisited=[(x,y) for y in range(self.size) for x in range(self.size)
                            if self.kb[y][x]['ok'] and not self.kb[y][x]['visited']]
            if safe_unvisited:
                best_path = None
                for cell in safe_unvisited:
                    path = self._find_path(self.pos, cell)
                    if path and (best_path is None or len(path) < len(best_path)):
                        best_path = path

                if best_path:
                    self.plan = self._path_to_actions(best_path)
                    action = self.plan.popleft()
                else:
                    dx, dy = DIRECTIONS[self.orientation]
                    nx, ny = self.pos[0] + dx, self.pos[1] + dy

                    valid_forward = self._is_valid(nx, ny) and not self.kb[ny][nx]['pit'] and self.kb[ny][nx]['wumpus'] != 'yes'

                    if valid_forward:
                        action = random.choice([ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_MOVE_FORWARD])
                    else:
                        action = random.choice([ACTION_TURN_LEFT, ACTION_TURN_RIGHT])
            else:
                target = self._get_least_risk_cell()
                print(f"[DEBUG] Chọn ô risk thấp nhất: {target}")

                if target:
                    path = self._find_risk_path(self.pos, target) 
                    print(f"[DEBUG] Đường đi tới {target}: {path}") 
                    self.plan = self._path_to_actions(path) 
                    action = self.plan.popleft()
                else:
                    target = self._get_least_risk_cell()
                    if target:
                        path = self._find_path(self.pos, target)
                        if path:
                            self.plan = self._path_to_actions(path)
                            action = self.plan.popleft()
                        else:
                            if self.pos != (0, 0):
                                path = self._find_path(self.pos, (0, 0))
                                if path:
                                    self.plan = self._path_to_actions(path)
                                    action = self.plan.popleft()
                                else:
                                    action = ACTION_CLIMB
                            else:
                                action = ACTION_CLIMB
                    else:
                        if self.pos != (0, 0):
                            path = self._find_path(self.pos, (0, 0))
                            if path:
                                self.plan = self._path_to_actions(path)
                                action = self.plan.popleft()
                            else:
                                action = ACTION_CLIMB
                        else:
                            action = ACTION_CLIMB

        if not self.has_gold:
            shoot_action = self._decide_shoot()
            if shoot_action:
                self.has_arrow = False
                dx, dy = DIRECTIONS[self.orientation]
                self.awaiting_scream = (dx, dy)
                action = shoot_action

        self.action_log.append(action)
        if action==ACTION_CLIMB:
            print("=== Action log ===")
            print(self.action_log)

        return action
