import os
import time
import numpy as np
from datetime import datetime

from config import *
from environment import WumpusWorld
from agent import HybridAgent, RandomAgent
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
        
        grid_repr = [list(row) for row in world.grid]
        for r in range(world.size):
            for c in range(world.size):
                if (c, r) == (0, 0) and grid_repr[r][c] == ' ':
                    grid_repr[r][c] = 'S'
        
        for row in grid_repr:
            f.write(' '.join(row) + '\n')
            
    print(f"Bản đồ đã được lưu vào: {filename}")
    
    all_maps = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.startswith('map_')])
    if len(all_maps) > 3:
        for old_map in all_maps[:-3]:
            os.remove(old_map)

def print_game_state(world, agent, percepts, last_action):
    """Hiển thị trạng thái trò chơi trên terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("="*40)
    print(f"WUMPUS WORLD - TERMINAL VERSION")
    print("="*40)
    print(f"Score: {world.score} | Last Action: {last_action}")
    
    percept_str = ", ".join([p.upper() for p, v in percepts.items() if v])
    print(f"Percepts: {percept_str if percept_str else 'None'}")
    print("-" * 40)

    for r in range(world.size):
        for c in range(world.size):
            cell_str = ''
            if agent.pos == (c, r):
                if agent.orientation == 'up': cell_str = ' ^A '
                elif agent.orientation == 'down': cell_str = ' vA '
                elif agent.orientation == 'left': cell_str = ' <A '
                else: cell_str = ' >A '
            elif not agent.kb[r][c]['visited']:
                cell_str = ' ? '
            else:
                cell_content = world.grid[r, c]
                if cell_content == 'G': cell_str = '  G '
                elif cell_content == 'P': cell_str = '  P '
                elif cell_content == 'W': cell_str = '  W '
                else: cell_str = ' . '
            
            print(f"|{cell_str}", end="")
        print("|")
    print("-" * 40)
    print("Legend: A=Agent,?=Unknown,.=Safe, G=Gold, P=Pit, W=Wumpus")
    print("-" * 40)

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
        print(f"Đã khởi tạo Hybrid Agent với thuật toán: {planning_algorithm.upper()}")
    else:
        agent = RandomAgent(size=GRID_SIZE)
        print("Đã khởi tạo Random Agent.")
        
    time.sleep(2)

    last_action = "Start"
    
    while not world.game_over:
        current_percepts = world.get_percepts()
        
        if isinstance(agent, HybridAgent):
            print_game_state(world, agent, current_percepts, last_action)
        
        agent.update_kb(current_percepts, last_action)
        
        if current_percepts['glitter']:
            action = ACTION_GRAB
        else:
            action = agent.choose_action()

        world.execute_action(action)
        last_action = action
        
        if isinstance(agent, RandomAgent):
            print(f"Random Agent action: {last_action}, Score: {world.score}")

        time.sleep(1)

    print("\n" + "="*40)
    print("GAME OVER!")
    print(f"Final Outcome: {world.game_outcome}")
    print(f"Final Score: {world.score}")
    print("="*40)


if __name__ == '__main__':
    main()