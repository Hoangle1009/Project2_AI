import os
import time
from datetime import datetime
from colorama import init, Fore, Style

from config import *
from environment import WumpusWorld
from agent import HybridAgent, RandomAgent
from terminal_display import print_live_map, print_final_map

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

        for r in reversed(range(world.size)):
            row_repr = []
            for c in range(world.size):
                cell = world.grid[r][c]
                if (c, r) == (0, 0) and cell == ' ':
                    row_repr.append('S') 
                elif (c, r) == world.agent_pos:
                    row_repr.append('A') 
                else:
                    row_repr.append(cell)
            f.write(' '.join(row_repr) + '\n')

    print(f"Bản đồ đã được lưu vào: {filename}")

    all_maps = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.startswith('map_')])
    if len(all_maps) > 3:
        for old_map in all_maps[:-3]:
            os.remove(old_map)


def get_user_choices():
    """Lấy lựa chọn của người dùng về tác tử và thuật toán."""
    agent_type = ''
    planning_algo = None
    move_wumpus = ' '
    while agent_type not in ['1', '2']:
        agent_type = input("Chọn loại tác tử (1: Hybrid, 2: Random): ")
    
    if agent_type == '1':
        agent_type = 'hybrid'
        while planning_algo not in ['astar', 'bfs']:
            planning_algo = input("Chọn thuật toán cho Hybrid Agent (astar, bfs): ").lower()
    else:
        agent_type = 'random'
    while move_wumpus not in ['y','n']:
        move_wumpus = input("Cho phép Wumpus di chuyển không? (y/n): ").lower()

    return agent_type, planning_algo, (move_wumpus=='y')
def main():
    agent_type, planning_algorithm, wumpus_can_move = get_user_choices()
    world = WumpusWorld(size=GRID_SIZE, pit_prob=PIT_PROBABILITY, moving_wumpus=wumpus_can_move)
    save_map_to_file(world)

    if agent_type == 'hybrid':
        agent = HybridAgent(size=GRID_SIZE, planning_algorithm=planning_algorithm)
        print(f"{Fore.YELLOW}Đã khởi tạo Hybrid Agent với thuật toán: {planning_algorithm.upper()}{Style.RESET_ALL}")
    else:
        agent = RandomAgent(size=GRID_SIZE)
        

    time.sleep(1)
    last_action = "Start"
    turn = 0
    action_count = 0
    while not world.game_over:
        if action_count ==5:
            action_count = 0
        current_percepts = world.get_percepts()
        agent.update_kb(current_percepts, last_action)

        if current_percepts['glitter']:
            action = ACTION_GRAB
        else:
            action = agent.choose_action()

        world.execute_action(action)
        action_count += 1

        if world.moving_wumpus and action_count % 5 == 0:
            world._move_all_wumpuses()
        last_action = action
        if(last_action == ACTION_SHOOT):
            world._shoot_arrow()
        if isinstance(agent, RandomAgent):
            print(f"{Fore.CYAN}Random Agent action: {last_action}, Score: {world.score}{Style.RESET_ALL}")
        if turn > 0:
            print_live_map(world, agent, current_percepts, last_action)
        turn += 1
        time.sleep(0.5) 
    print_final_map(world, agent)

    print("\n" + "="*40)
    print(f"{Fore.GREEN}GAME OVER!{Style.RESET_ALL}")
    print(f"Final Outcome: {world.game_outcome}")
    print(f"Final Score: {world.score}")
    print(agent.action_log)
    print("="*40)

if __name__ == '__main__':
    main()

