Code Review Notes – Wumpus Agents
1. RandomAgent

Mục đích: baseline agent, chọn hành động ngẫu nhiên.

KB: không sử dụng, chỉ thêm pos, orientation, kb để terminal live map hoạt động.

Action: [Move Forward, Turn Left, Turn Right, Grab, Shoot, Climb] ngẫu nhiên.

Inference: không có.

Live map: hiển thị agent, unknown, safe, vàng, pit, Wumpus (dựa trên vị trí và kb).

2. HybridAgent

Mục đích: agent thông minh, sử dụng KB và inference engine để quyết định an toàn.

KB Structure:

kb[y][x] = {
    'visited': bool,
    'ok': bool,         # safe to enter
    'wumpus': '?/yes?/no',
    'pit': '?/yes?/no'
}


Inference Engine: cập nhật trạng thái ô (safe, dangerous, uncertain) dựa trên percepts và KB rules.

Update KB:

Di chuyển: cập nhật pos và orientation.

Grab/Shoot: cập nhật has_gold, has_arrow.

Neighbor update theo percepts (stench, breeze, glitter, scream).

Reset Wumpus knowledge mỗi 5 action để xử lý di chuyển Wumpus.

Path Planning: skeleton _find_path (A* hoặc BFS cần implement). _convert_path_to_actions chuyển path → hành động.

Choose Action:

Thực hiện plan nếu có.

Nếu có vàng → về start → climb.

Chọn ô an toàn chưa thăm gần nhất.

Fallback: random safe action.

3. Terminal Live Map

Hiển thị liên tục vị trí agent, trạng thái cell (unknown, safe, vàng, pit, Wumpus).

RandomAgent và HybridAgent đều có thể hiển thị vì đều có pos, orientation, kb.
