import os
import time
from datetime import datetime
from colorama import init, Fore, Style

from config import *
from environment import WumpusWorld
from agent import HybridAgent, RandomAgent
from terminal_display import print_live_map

# Khởi tạo colorama cho Windows
init(autoreset=True)

def save_map_to_file(world, folder='testcases'):
    """Lưu cấu hình bản đồ hiện tại vào một tệp văn bản."""
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"map_{timestamp}.txt")

    with open(filename, 'w') as f:
        f.write(f"Size: {world.size}x{world.size}\n")
        f.write(f"Wumpus: {world.wumpus_positions}\n")
        f.write(f"Pits: {world.pit_pos}\n")
        f.write(f"Gold: {world.gold_pos}\n\n")

        for r in range(world.size):
            row_repr = []
            for c in range(world.size):
                cell = world.grid[r][c]
                if (c, r) == (0, 0) and cell == ' ':
                    row_repr.append('S')
                else:
                    row_repr.append(cell)
            f.write(' '.join(row_repr) + '\n')

    print(f"Bản đồ đã được lưu vào: {filename}")

    # Giữ lại 3 bản đồ gần nhất
    all_maps = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.startswith('map_')])
    if len(all_maps) > 3:
        for old_map in all_maps[:-3]:
            os.remove(old_map)

def get_user_choices():
    """Lấy lựa chọn của người dùng về tác tử và thuật toán."""
    agent_type = ''
    planning_algo = None
    while agent_type not in ['1', '2']:
        agent_type = input("Chọn loại tác tử (1: Hybrid, 2: Random): ")
    
    if agent_type == '1':
        agent_type = 'hybrid'
        while planning_algo not in ['astar', 'bfs']:
            planning_algo = input("Chọn thuật toán cho Hybrid Agent (astar, bfs): ").lower()
    else:
        agent_type = 'random'
    return agent_type, planning_algo

def main():
    agent_type, planning_algorithm = get_user_choices()
    world = WumpusWorld(size=GRID_SIZE, pit_prob=PIT_PROBABILITY)
    save_map_to_file(world)

    if agent_type == 'hybrid':
        agent = HybridAgent(size=GRID_SIZE, planning_algorithm=planning_algorithm)
        print(f"{Fore.YELLOW}Đã khởi tạo Hybrid Agent với thuật toán: {planning_algorithm.upper()}{Style.RESET_ALL}")
    else:
        agent = RandomAgent(size=GRID_SIZE)
        # Thêm pos và kb để terminal print không lỗi
        agent.pos = (0, 0)
        agent.orientation = 'right'
        agent.kb = [[{'visited': False} for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        print(f"{Fore.CYAN}Đã khởi tạo Random Agent.{Style.RESET_ALL}")

    time.sleep(1)
    last_action = "Start"

    while not world.game_over:
        current_percepts = world.get_percepts()
        # Hiển thị live map cho mọi agent
        print_live_map(world, agent, current_percepts, last_action)
            
        agent.update_kb(current_percepts, last_action)

        if current_percepts['glitter']:
            action = ACTION_GRAB
        else:
            action = agent.choose_action()

        world.execute_action(action)
        last_action = action

        if isinstance(agent, RandomAgent):
            print(f"{Fore.CYAN}Random Agent action: {last_action}, Score: {world.score}{Style.RESET_ALL}")

        time.sleep(0.5)  # Cập nhật nhanh cho demo

    print("\n" + "="*40)
    print(f"{Fore.GREEN}GAME OVER!{Style.RESET_ALL}")
    print(f"Final Outcome: {world.game_outcome}")
    print(f"Final Score: {world.score}")
    print("="*40)

if __name__ == '__main__':
    main()
