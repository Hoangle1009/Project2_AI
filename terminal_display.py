from config import *

# ANSI màu
COLOR_MAP = {
    'agent': '\033[93m',      # vàng
    'gold': '\033[33m',       # vàng đậm
    'pit': '\033[41m',        # đỏ nền
    'wumpus': '\033[45m',     # tím nền
    'safe': '\033[42m',       # xanh nền
    'unknown': '\033[100m',   # xám nền
    'reset': '\033[0m'
}

def print_live_map(world, agent, percepts, last_action):
    """Hiển thị map live trong terminal với màu sắc và hướng agent."""
    # clear terminal
    # print("\033[H\033[J", end='')

    print("="*50)
    print(f"WUMPUS WORLD - TERMINAL VERSION")
    print("="*50)
    print(f"Score: {world.score} | Last Action: {last_action}")
    percept_str = ", ".join([p.upper() for p, v in percepts.items() if v])
    print(f"Percepts: {percept_str if percept_str else 'None'}")
    print("-"*50)
    world.print_position()

    orientation_symbol = {
        "up": "^",
        "down": "v",
        "left": "<",
        "right": ">"
    }

    for r in range(world.size - 1, -1, -1):
        for c in range(world.size):
            cell_char = "   "
            cell_color = COLOR_MAP['unknown']

            if agent.pos == (c, r):
                cell_char = f" {orientation_symbol[agent.orientation]} "
                cell_color = COLOR_MAP['agent']
            elif not agent.kb[r][c]['visited']:
                cell_char = " ? "
                cell_color = COLOR_MAP['unknown']
            else:
                content = world.grid[r, c]
                if content == 'G':
                    cell_char = ' G '
                    cell_color = COLOR_MAP['gold']
                elif content == 'P':
                    cell_char = ' P '
                    cell_color = COLOR_MAP['pit']
                elif content == 'W':
                    cell_char = ' W '
                    cell_color = COLOR_MAP['wumpus']
                else:
                    cell_char = ' . '
                    cell_color = COLOR_MAP['safe']

            print(f"{cell_color}{cell_char}{COLOR_MAP['reset']}", end='')
        print()
    print("-"*50)
    print("Legend: ^v<> = Agent hướng, ?=Unknown, .=Safe, G=Gold, P=Pit, W=Wumpus")
    print("-"*50)
