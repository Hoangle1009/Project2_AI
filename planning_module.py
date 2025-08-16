import heapq
from collections import deque

def bfs_path(start, goal, safe_cells, size):
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path

        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) in safe_cells and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path+[(nx, ny)]))

    return None


def astar_path(start, goal, safe_cells, size, cost_map=None):
    """
    Find optimal path using A* search with Manhattan heuristic.
    - cost_map: dict {(x,y): cost}, optional (default cost = 1)
    """
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = [(heuristic(start, goal), 0, start, [start])]
    visited = {}

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        if current == goal:
            return path

        if current in visited and visited[current] <= g:
            continue
        visited[current] = g

        x, y = current
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) in safe_cells:
                step_cost = cost_map.get((nx, ny), 1) if cost_map else 1
                heapq.heappush(open_set, (
                    g + step_cost + heuristic((nx,ny), goal),
                    g + step_cost,
                    (nx, ny),
                    path+[(nx, ny)]
                ))

    return None
