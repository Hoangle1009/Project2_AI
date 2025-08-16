import heapq
from collections import deque

def _neighbors(x, y, size):
    for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < size and 0 <= ny < size:
            yield nx, ny

def bfs_path(start, goal, safe_cells, size):
    safe = set(safe_cells)
    safe.add(start)
    safe.add(goal)

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        for nx, ny in _neighbors(x, y, size):
            nxt = (nx, ny)
            if nxt not in visited and nxt in safe:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None

def astar_path(start, goal, safe_cells, size, cost_map=None):
    safe = set(safe_cells)
    safe.add(start)
    safe.add(goal)

    def h(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = [(h(start, goal), 0, start, [start])]
    best_g = {start: 0}
    cost_map = cost_map or {}

    while open_set:
        f, g, (x, y), path = heapq.heappop(open_set)
        if (x, y) == goal:
            return path

        if best_g.get((x, y), float('inf')) < g:
            continue

        for nx, ny in _neighbors(x, y, size):
            nxt = (nx, ny)
            if nxt not in safe:
                continue
            step = cost_map.get(nxt, 1)
            ng = g + step
            if ng < best_g.get(nxt, float('inf')):
                best_g[nxt] = ng
                nf = ng + h(nxt, goal)
                heapq.heappush(open_set, (nf, ng, nxt, path + [nxt]))
    return None
