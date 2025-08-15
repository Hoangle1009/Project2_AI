from config import *

class InferenceEngine:
    """
    Inference Engine cho Hybrid Agent.
    Sử dụng forward chaining để cập nhật KB dựa trên percepts.
    """

    def __init__(self, size=GRID_SIZE):
        self.size = size
        # KB: mỗi cell lưu thông tin {'visited', 'ok', 'wumpus', 'pit', 'glitter'}
        self.kb = [[{'visited': False, 'ok': False, 'wumpus': '?', 'pit': '?', 'glitter': False}
                    for _ in range(size)] for _ in range(size)]
        # Wumpus còn sống
        self.wumpus_alive = True

    def _is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def _get_adjacent_cells(self, x, y):
        """Trả về danh sách ô lân cận hợp lệ"""
        adjacent = []
        for dx, dy in DIRECTIONS.values():
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny):
                adjacent.append((nx, ny))
        return adjacent

    def update_knowledge(self, pos, percepts):
        """Cập nhật KB dựa trên percepts từ ô hiện tại"""
        x, y = pos
        cell = self.kb[y][x]

        # 1. Đánh dấu ô hiện tại đã thăm
        cell['visited'] = True
        cell['ok'] = True
        cell['glitter'] = percepts['glitter']

        neighbors = self._get_adjacent_cells(x, y)

        # 2. Scream → Wumpus chết
        if percepts['scream']:
            self.wumpus_alive = False
            for r in range(self.size):
                for c in range(self.size):
                    self.kb[r][c]['wumpus'] = 'no'

        # 3. Stench → Wumpus có thể ở ô lân cận
        if self.wumpus_alive:
            if percepts['stench']:
                for nx, ny in neighbors:
                    if self.kb[ny][nx]['wumpus'] == '?':
                        self.kb[ny][nx]['wumpus'] = 'maybe'
            else:
                for nx, ny in neighbors:
                    self.kb[ny][nx]['wumpus'] = 'no'

        # 4. Breeze → Pit có thể ở ô lân cận
        if percepts['breeze']:
            for nx, ny in neighbors:
                if self.kb[ny][nx]['pit'] == '?':
                    self.kb[ny][nx]['pit'] = 'maybe'
        else:
            for nx, ny in neighbors:
                self.kb[ny][nx]['pit'] = 'no'

        # 5. Forward chaining: nếu ô lân cận đã loại bỏ pit và wumpus → đánh dấu safe
        for nx, ny in neighbors:
            neighbor = self.kb[ny][nx]
            if neighbor['wumpus'] in ['no'] and neighbor['pit'] in ['no']:
                neighbor['ok'] = True
            else:
                neighbor['ok'] = False

    def is_safe(self, x, y):
        """Trả về True nếu ô safe"""
        return self.kb[y][x]['ok']

    def cell_status(self, x, y):
        """Trả về trạng thái cell: 'safe', 'danger', 'unknown'"""
        if self.kb[y][x]['ok']:
            return 'safe'
        if self.kb[y][x]['wumpus'] == 'maybe' or self.kb[y][x]['pit'] == 'maybe':
            return 'danger'
        return 'unknown'
